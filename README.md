# ebrains-downloader

## A CLI tool for downloading whole-slide images from EBRAINS

A command-line tool to download `.ndpi` files from an EBRAINS dataset, filtered by diagnosis name.

[article link](https://hokumedai.github.io/articles/tech-stack/ebrains-downloader/)

## Installation

No installation required. Run directly from GitHub with [uvx](https://docs.astral.sh/uv/):

```bash
uvx --from git+https://github.com/HokuMedAI/ebrains-downloader ebrains-downloader --diagnosis <DIAGNOSIS>
```

<details>
<summary>Local install</summary>

```bash
git clone https://github.com/HokuMedAI/ebrains-downloader
cd ebrains-downloader

# uv
uv sync

# venv
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

</details>

## Basic use

```bash
uvx --from git+https://github.com/HokuMedAI/ebrains-downloader ebrains-downloader --diagnosis <DIAGNOSIS> [OPTIONS]
```

### Auguments

| Argument | Description | Default |
|---|---|---|
| `--diagnosis` | One or more diagnosis names to download (required) | — |
| `--output` | Output directory | `downloads` |

Download all files for a single diagnosis:

```bash
uvx --from git+https://github.com/HokuMedAI/ebrains-downloader ebrains-downloader --diagnosis Meningioma
```

Download files for multiple diagnoses:

```bash
uvx --from git+https://github.com/HokuMedAI/ebrains-downloader ebrains-downloader --diagnosis Meningioma Schwannoma
```

Diagnosis names containing spaces must be quoted:

```bash
uvx --from git+https://github.com/HokuMedAI/ebrains-downloader ebrains-downloader --diagnosis "Fibrous meningioma"
```

Specify a custom output directory:

```bash
uvx --from git+https://github.com/HokuMedAI/ebrains-downloader ebrains-downloader --diagnosis Meningioma --output /data/ebrains
```


### Authentication

Authentication is handled automatically via `fairgraph`. You will be prompted to log in to your EBRAINS account on first use.

### Output structure

Downloaded files and the annotation CSV are saved under the output directory:

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

### Auto-resume

Interrupted downloads are automatically resumed from where they left off.

## Issues

Please report bugs and feature requests at [GitHub Issues](https://github.com/HokuMedAI/ebrains-downloader/issues). 
