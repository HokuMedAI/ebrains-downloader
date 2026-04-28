import argparse
import csv
import sys
from pathlib import Path
from urllib.parse import quote

import requests
from fairgraph import KGClient
from tqdm import tqdm

DATASET_ID = "8fc108ab-e2b4-406f-8999-60269dc1f994"
VERSION = "v1.0"
BASE_URL = f"https://data-proxy.ebrains.eu/api/v1/datasets/{DATASET_ID}/{VERSION}"

MAX_RETRIES = 5
TIMEOUT = (30, 60)  # (connect, read) seconds


def get_token() -> str:
    client = KGClient(host="core.kg.ebrains.eu")
    return client.token


def download_annotation(token: str, dest: Path) -> None:
    url = f"{BASE_URL}/annotation.csv"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT)
    resp.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    print(f"Downloaded annotation: {dest}")


def load_targets(annotation_path: Path, diagnoses: list[str]) -> list[tuple[str, str]]:
    diagnoses_lower = {d.lower() for d in diagnoses}
    targets = []
    with open(annotation_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            diagnosis = row["diagnosis"].strip()
            if diagnosis.lower() in diagnoses_lower:
                targets.append((diagnosis, row["uuid"].strip()))
    return targets


def download_file(token: str, diagnosis: str, uuid: str, output_dir: Path, index: int, total: int) -> None:
    url = f"{BASE_URL}/{quote(diagnosis)}/{uuid}.ndpi"
    dest = output_dir / diagnosis / f"{uuid}.ndpi"
    dest.parent.mkdir(parents=True, exist_ok=True)
    desc = f"[{index}/{total}] {uuid}"

    for attempt in range(1, MAX_RETRIES + 1):
        resumed = dest.exists() and dest.stat().st_size > 0
        offset = dest.stat().st_size if resumed else 0

        headers = {"Authorization": f"Bearer {token}"}
        if resumed:
            headers["Range"] = f"bytes={offset}-"

        try:
            resp = requests.get(url, headers=headers, stream=True, timeout=TIMEOUT)
            if resp.status_code == 416:  # already complete
                tqdm.write(f"  skip (already complete): {dest}")
                return
            resp.raise_for_status()

            total_size = int(resp.headers.get("Content-Length", 0)) + offset
            mode = "ab" if resumed else "wb"

            with (
                open(dest, mode) as f,
                tqdm(total=total_size, initial=offset, unit="B", unit_scale=True, unit_divisor=1024, desc=desc) as bar,
            ):
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
                    bar.update(len(chunk))
            return

        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError) as e:
            if attempt == MAX_RETRIES:
                raise
            tqdm.write(f"\n  retry {attempt}/{MAX_RETRIES}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Download EBRAINS dataset files filtered by diagnosis")
    parser.add_argument("--diagnosis", nargs="+", required=True, metavar="DIAGNOSIS", help="Diagnosis name(s) to download")
    parser.add_argument("--refresh-annotation", action="store_true", help="Re-download annotation.csv even if it exists")
    parser.add_argument("--output", default="downloads", help="Output directory (default: downloads)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    annotation_path = output_dir / "annotation.csv"

    token = get_token()

    if not annotation_path.exists() or args.refresh_annotation:
        print("Downloading annotation.csv...")
        download_annotation(token, annotation_path)

    print(f"Filtering diagnoses: {args.diagnosis}")
    targets = load_targets(annotation_path, args.diagnosis)
    if not targets:
        print("No matching UUIDs found for the given diagnosis name(s).")
        sys.exit(0)
    print(f"Found {len(targets)} matching UUID(s)")

    print(f"Downloading {len(targets)} file(s)...")
    failed = []
    for i, (diagnosis, uuid) in enumerate(targets, 1):
        try:
            download_file(token, diagnosis, uuid, output_dir, i, len(targets))
        except Exception as e:
            tqdm.write(f"  FAILED: {diagnosis}/{uuid} ({e})", file=sys.stderr)
            failed.append(f"{diagnosis}/{uuid}")

    print(f"\nDone. {len(targets) - len(failed)} succeeded, {len(failed)} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
