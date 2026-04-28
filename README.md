# EBRAINS Downloader

A command-line tool to download whole-slide images from an EBRAINS dataset, filtered by diagnosis.

## Requirements

- Python 3.10+
- [fairgraph](https://github.com/HumanBrainProject/fairgraph)
- requests
- tqdm

Install dependencies:

```bash
# uv
uv sync

# pip
pip install fairgraph requests tqdm
```

## Configuration

Before using the tool, set the following constants in `run.py` to match your target dataset:

```python
DATASET_ID = "..."   # EBRAINS dataset ID
VERSION    = "..."   # Dataset version
BASE_URL   = "..."   # Base URL to the dataset
```

## Authentication

Authentication is handled automatically via `fairgraph`. You will be prompted to log in to your EBRAINS account on first use.

## Usage

```bash
# uv
uv run run.py --diagnosis <DIAGNOSIS> [OPTIONS]

# pip
python run.py --diagnosis <DIAGNOSIS> [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|---|---|---|
| `--diagnosis` | One or more diagnosis names to download (required) | — |
| `--output` | Output directory | `downloads` |
| `--refresh-annotation` | Re-download `annotation.csv` even if it already exists | off |

### Examples

Download all files for a single diagnosis:

```bash
uv run run.py --diagnosis Meningioma
```

Download files for multiple diagnoses:

```bash
uv run run.py --diagnosis Meningioma Schwannoma
```

Diagnosis names containing spaces must be quoted:

```bash
uv run run.py --diagnosis "Fibrous meningioma"
```

Specify a custom output directory:

```bash
uv run run.py --diagnosis Meningioma --output /data/ebrains
```

Force re-download of the annotation file:

```bash
uv run run.py --diagnosis Meningioma --refresh-annotation
```

## Output Structure

Downloaded files are saved under the output directory, organized by diagnosis:

```
downloads/
├── annotation.csv
├── Meningioma/
│   ├── <uuid>.ndpi
│   └── ...
└── Fibrous meningioma/
    ├── <uuid>.ndpi
    └── ...
```

## Resume Support

Interrupted downloads are automatically resumed from where they left off. Re-running the same command will skip already-completed files.
