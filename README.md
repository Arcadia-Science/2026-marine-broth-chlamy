# Marine Broth Chlamydomonas Image Processing Tools

[![run with conda](https://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/projects/miniconda/en/latest/)

## Purpose

This repository provides image processing tools for RGB brightfield and fluorescence microscopy images of *Chlamydomonas smithii* cultures grown in marine broth conditions. It includes two Python scripts for batch processing (flat-field correction and structure enhancement) and one interactive Jupyter notebook for multi-channel image alignment with example data.

**Associated Publication:** "Marine Broth induces extreme morphological transformations in Chlamydomonas smithii" https://doi.org/10.57844/arcadia-q58n-51bk

**Associated Data:** Microscopy data is available on the BioImage Archive doi: 10.6019/S-BIAD2873

## Installation and Setup

This repository uses conda to manage software environments and installations. You can find operating system-specific instructions for installing miniconda [here](https://docs.conda.io/projects/miniconda/en/latest/). After installing conda and [mamba](https://mamba.readthedocs.io/en/latest/), run the following command to create the pipeline run environment.

```bash
mamba env create -n chlamy-imaging --file envs/dev.yml
conda activate chlamy-imaging
```

Alternatively, you can use pip to install dependencies:

```bash
pip install -r requirements.txt
```

<details><summary>Developer Notes (click to expand/collapse)</summary>

1. Install your pre-commit hooks:

    ```{bash}
    pre-commit install
    ```

    This installs the pre-commit hooks defined in your config (`./.pre-commit-config.yaml`).

2. Export your conda environment before sharing:

    As your project develops, the number of dependencies in your environment may increase. Whenever you install new dependencies (using either `pip install` or `mamba install`), you should update the environment file using the following command.

    ```{bash}
    conda env export --no-builds > envs/dev.yml
    ```

    `--no-builds` removes build specification from the exported packages to increase portability between different platforms.
</details>

## Data

### Example Data

Example images are provided in the `data/` directory to demonstrate the channel alignment workflow:
- `Sample_Chlorophyll_Cy5.tif` - Chlorophyll autofluorescence channel (reference)
- `Sample_PKmito_TRITC.tif` - Mitochondrial marker channel (to be aligned)

These are 23-slice z-stacks (388 × 304 pixels, 16-bit) showing chromatic aberration that can be corrected using the alignment notebook.

- `Sample_Wisp_Timelapse.tif` - Grayscale timelapse of a wisp extending from a cell body (to be revealed). This is a 10 frame snippet of the file "MB_1xMT_30min_NoWash_TL_002.nd" available on BioImage Archive (DOI: 10.6019/S-BIAD2873)
- `Sample_LIDA.tif` - RGB composite image of Chlamydomonas cells grown on water + agar and imaged with the LIDA light engine. A Red to Blue gradient covers the field of view.



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
├── envs/                    # Conda environment specifications
├── requirements.txt         # pip dependencies
└── README.md               # This file
```

### Tools

#### 1. Flat-Field Correction (`scripts/smoothen_lida_rgb_tifs.py`)

Python script for batch correction of uneven illumination from LED light engines using Gaussian blur-based background estimation. **Includes example data** to demonstrate the workflow.

**Key features:**
- Batch processing of multi-channel images
- Preserves original bit depth
- Configurable blur sigma for different correction strengths

**Usage:**
```bash
python scripts/smoothen_lida_rgb_tifs.py
```
Edit the configuration section at the top of the script to set your input directory and parameters.

#### 2. Channel Alignment (`notebooks/realign_channels_clean.ipynb`)

Interactive Jupyter notebook for aligning fluorescence channels affected by chromatic aberration. **Includes example data** to demonstrate the workflow.

**Key features:**
- Phase cross-correlation for automatic shift detection
- Interactive sliders for manual fine-tuning
- Real-time preview with zoom capability
- Display-only brightness/contrast adjustments (exports preserve original intensities)
- Example images provided in `data/` directory

**Usage:**
```bash
jupyter lab notebooks/realign_channels_clean.ipynb
```
The notebook is pre-configured to run on the example data. Edit the configuration cell to process your own images.

#### 3. Structure Enhancement (`scripts/reveal_wisps.py`)

Python script for revealing fine cellular structures through unsharp masking, CLAHE, and temporal smoothing. **Includes example data** to demonstrate workflow.

**Key features:**
- Multi-step enhancement pipeline
- Temporal smoothing across time series
- Annotated video export with scale bars
- Side-by-side before/after comparisons

**Usage:**
```bash
python scripts/reveal_wisps.py
```
Edit the configuration section at the top of the script to set your file paths and parameters.

### Usage

#### For Python Scripts (Batch Processing)

1. Edit the configuration section at the top of the script with your file paths and parameters

2. Run the script:
   ```bash
   python scripts/smoothen_lida_rgb_tifs.py
   # or
   python scripts/reveal_wisps.py
   ```

Scripts follow a consistent structure:
- **Configuration Section**: Set input/output paths and processing parameters at the top
- **Processing Functions**: Main image processing logic
- **Main Block**: Batch processing loop

#### For Interactive Notebook (Channel Alignment)

1. Launch Jupyter Lab:
   ```bash
   jupyter lab
   ```

2. Open `notebooks/realign_channels_clean.ipynb`

3. Run the notebook with example data (pre-configured) or edit the configuration cell for your own images

4. Use interactive sliders to fine-tune alignment, then export results

The notebook workflow:
- **Configuration Cell**: Set input/output paths (defaults to example data)
- **Interactive Cell**: Load images and use sliders to find optimal alignment
- **Export Cell**: Save aligned results

### Compute Specifications

These notebooks were developed and tested on:
- **Operating System**: macOS (Darwin 23.5.0)
- **Hardware**: Standard desktop/laptop computing resources
- **RAM**: 16+ GB recommended for processing large image stacks
- **Storage**: Variable depending on dataset size; processed outputs typically similar in size to inputs

Processing time depends on image dimensions and stack depth. Typical operations complete within minutes on modern hardware.

## Contributing

See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide--credit-for-contributions.md).

---
## For Developers

This section contains information for developers who are working off of this template. Please adjust or edit this section as appropriate when you're ready to share your repo.

### GitHub templates
This template uses GitHub templates to provide checklists when making new pull requests. These templates are stored in the [.github/](./.github/) directory.

### VSCode
This template includes recommendations to VSCode users for extensions, particularly the `ruff` linter. These recommendations are stored in `.vscode/extensions.json`. When you open the repository in VSCode, you should see a prompt to install the recommended extensions.

### `.gitignore`
This template uses a `.gitignore` file to prevent certain files from being committed to the repository.

### `pyproject.toml`
`pyproject.toml` is a configuration file to specify your project's metadata and to set the behavior of other tools such as linters, type checkers etc. You can learn more [here](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### Linting
This template automates linting and formatting using GitHub Actions and the `ruff` linter. When you push changes to your repository, GitHub will automatically run the linter and report any errors, blocking merges until they are resolved.
