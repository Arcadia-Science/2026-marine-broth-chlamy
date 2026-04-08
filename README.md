# Marine Broth Chlamydomonas Image Processing Tools

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

## Purpose

This repository provides image processing tools for RGB brightfield and fluorescence microscopy images of *Chlamydomonas smithii* cultures grown in marine broth conditions. It includes two Python scripts for batch processing (flat-field correction and structure enhancement) and one interactive Jupyter notebook for multi-channel image alignment with example data.

**Associated Publication:** "Marine Broth induces extreme morphological transformations in Chlamydomonas smithii" https://doi.org/10.57844/arcadia-q58n-51bk

**Associated Data:** Microscopy data is available on the BioImage Archive doi: 10.6019/S-BIAD2873

## Installation and Setup

This repository uses [uv](https://docs.astral.sh/uv/) to manage dependencies and virtual environments. Install uv following the [official instructions](https://docs.astral.sh/uv/getting-started/installation/), then run:

```bash
uv sync
```

This creates a `.venv` virtual environment and installs all runtime dependencies. To also install dev tools (ruff, pre-commit):

```bash
uv sync --group dev
```

<details><summary>Developer Notes (click to expand/collapse)</summary>

1. Install your pre-commit hooks:

    ```bash
    uv run pre-commit install
    ```

    This installs the pre-commit hooks defined in your config (`./.pre-commit-config.yaml`).

2. Adding new dependencies:

    ```bash
    uv add <package>              # runtime dependency
    uv add --group dev <package>  # dev-only dependency
    ```

    This updates `pyproject.toml` and `uv.lock` automatically.
</details>

## Data

### Example Data

Example images are provided in the `data/` directory to demonstrate the channel alignment workflow. Example data has been cropped to reduce the file size in this repo. Full data is available at https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD2873.

These are 23-slice z-stacks (388 × 304 pixels, 16-bit) showing chromatic aberration that can be corrected using the alignment notebook (realign_channels_clean.ipynb). Both images are from the same z-stack acquired with different fluorescence channels. The raw ND2 source file is available as MB_10xPK_30min_NoWash_Fluor_zstack_005.nd2 on BioImage Archive (DOI: 10.6019/S-BIAD2873).
- `Sample_Chlorophyll_Cy5.tif` - Chlorophyll autofluorescence channel (reference)
- `Sample_PKmito_TRITC.tif` - Mitochondrial marker channel (to be aligned)

Grayscale timelapse of a wisp extending from a cell body. This is an example file to run reveal_wisps.py. This is a 10 frame snippet of the file "MB_1xMT_30min_NoWash_TL_002.nd" available on BioImage Archive (DOI: 10.6019/S-BIAD2873). 
- `Sample_Wisp_Timelapse.tif`

RGB composite image of Chlamydomonas cells grown on water + agar and imaged with the LIDA light engine. A Red to Blue gradient covers the field of view. smoothen_lida_rgb_tifs.py can be used to remove this background gradient. The raw ND2 file can be found in the "40-day cultures across media types" study component on BioImage Archive (DOI: 10.6019/S-BIAD2873) as Water_001.nd2.
- `Sample_LIDA.tif` 



### Input Data

The tools process fluorescence microscopy images with the following specifications:
- **File formats**: TIF/TIFF (8-bit or 16-bit)
- **Image types**: Grayscale, multi-channel (RGB, Cy5/TRITC, etc.), z-stacks, time series
- **Typical image size**: 2304 × 2304 pixels (example data is smaller for repository size)
- **Acquisition**: Images acquired using LED light engines (e.g., Lida) and fluorescence microscopy

### Output Data

Processed outputs include:
- Flat-field corrected TIFF stacks
- Aligned multi-channel images
- Enhanced structure visualizations
- Annotated video exports with scale bars and timestamps

## Overview

### Description of the folder structure

```
.
├── data/                    # Example microscopy images
│   ├── Sample_Chlorophyll_Cy5.tif        # Example chlorophyll channel
|   ├── Sample_LIDA.tif                   # Example RGB composite image
│   ├── Sample_PKmito_TRITC.tif           # Example mitochondrial channel
|   └── Sample_Wisp_Timelapse.tif         # Example timelapse of motile wisps  
├── notebooks/               # Interactive Jupyter notebooks
│   └── realign_channels_clean.ipynb      # Multi-channel alignment (with examples)
├── scripts/                 # Python scripts for batch processing
│   ├── reveal_wisps.py                   # Structure enhancement & video export
│   └── smoothen_lida_rgb_tifs.py         # Flat-field illumination correction
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Locked dependency versions
└── README.md
```

### Tools

#### 1. Flat-Field Correction (`scripts/smoothen_lida_rgb_tifs.py`)

Python script for batch correction of uneven illumination from LED light engines using Gaussian blur-based background estimation. Defaults to processing example data in `data/`.

**Key features:**
- Batch processing of multi-channel images
- Preserves original bit depth
- Configurable blur sigma for different correction strengths

**Usage:**

```bash
uv run python scripts/smoothen_lida_rgb_tifs.py                    # process example data
uv run python scripts/smoothen_lida_rgb_tifs.py --input-dir mydir  # custom directory
```

Run `uv run python scripts/smoothen_lida_rgb_tifs.py --help` for all options. Processing parameters can be adjusted at the top of the script.

#### 2. Channel Alignment (`notebooks/realign_channels_clean.ipynb`)

Interactive Jupyter notebook for aligning fluorescence channels affected by chromatic aberration. Includes example data to demonstrate the workflow.

**Key features:**
- Phase cross-correlation for automatic shift detection
- Interactive sliders for manual fine-tuning
- Real-time preview with zoom capability
- Display-only brightness/contrast adjustments (exports preserve original intensities)
- Example images provided in `data/` directory

**Usage:**
```bash
uv run jupyter lab notebooks/realign_channels_clean.ipynb
```
The notebook is pre-configured to run on the example data. Edit the configuration cell to process your own images.

#### 3. Structure Enhancement (`scripts/reveal_wisps.py`)

Python script for revealing fine cellular structures through unsharp masking, CLAHE, and temporal smoothing. Defaults to processing example data in `data/Sample_Wisp_Timelapse.tif`.

**Key features:**
- Multi-step enhancement pipeline
- Temporal smoothing across time series
- Annotated video export with scale bars
- Side-by-side before/after comparisons

**Usage:**
```bash
uv run python scripts/reveal_wisps.py                        # process example data
uv run python scripts/reveal_wisps.py --input my_stack.tif   # custom input
```

Run `uv run python scripts/reveal_wisps.py --help` for all options. Processing parameters can be adjusted at the top of the script.

### Compute Specifications

These notebooks were developed and tested on:
- **Operating System**: macOS (Darwin 23.5.0)
- **Hardware**: Standard desktop/laptop computing resources
- **RAM**: 16+ GB recommended for processing large image stacks
- **Storage**: Variable depending on dataset size; processed outputs typically similar in size to inputs

Processing time depends on image dimensions and stack depth. Typical operations complete within minutes on modern hardware.

## Contributing

See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide--credit-for-contributions.md).