# Marine Broth Chlamydomonas Image Processing Tools

[![run with conda](https://img.shields.io/badge/run%20with-conda-3EB049?labelColor=000000&logo=anaconda)](https://docs.conda.io/projects/miniconda/en/latest/)

## Purpose

This repository provides image processing tools for fluorescence microscopy analysis of *Chlamydomonas smithii* cultures grown in marine broth conditions. It includes three specialized Jupyter notebooks for correcting illumination artifacts, aligning multi-channel images, and revealing fine cellular structures in time-series data.

**Associated Publication:** "Marine Broth induces extreme morphological transformations in Chlamydomonas smithii" (forthcoming)

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

### Input Data

The notebooks process fluorescence microscopy images with the following specifications:
- **File formats**: TIF/TIFF (8-bit or 16-bit)
- **Image types**: Grayscale, multi-channel (RGB, Cy5/TRITC, etc.), z-stacks, time series
- **Typical image size**: 2304 × 2304 pixels
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
├── notebooks/               # Jupyter notebooks for image processing
│   ├── Smoothen_LIDA_RGB_TIfs.ipynb      # Flat-field illumination correction
│   ├── realign_channels_clean.ipynb       # Multi-channel alignment
│   └── reveal-wisps.ipynb                 # Structure enhancement & video export
├── envs/                    # Conda environment specifications
├── requirements.txt         # pip dependencies
└── README.md               # This file
```

### Notebooks

#### 1. Flat-Field Correction (`notebooks/Smoothen_LIDA_RGB_TIfs.ipynb`)

Corrects uneven illumination from LED light engines using Gaussian blur-based background estimation.

**Key features:**
- Batch processing of multi-channel images
- Preserves original bit depth
- Configurable blur sigma for different correction strengths

#### 2. Channel Alignment (`notebooks/realign_channels_clean.ipynb`)

Interactive tool for aligning fluorescence channels affected by chromatic aberration.

**Key features:**
- Phase cross-correlation for automatic shift detection
- Interactive sliders for manual fine-tuning
- Real-time preview with zoom capability
- Display-only brightness/contrast adjustments (exports preserve original intensities)

#### 3. Structure Enhancement (`notebooks/reveal-wisps.ipynb`)

Reveals fine cellular structures through unsharp masking, CLAHE, and temporal smoothing.

**Key features:**
- Multi-step enhancement pipeline
- Temporal smoothing across time series
- Annotated video export with scale bars
- Side-by-side before/after comparisons

### Methods

1. Launch Jupyter Lab:
   ```bash
   jupyter lab
   ```

2. Open the desired notebook from the `notebooks/` directory

3. Edit the configuration cell with your file paths and parameters

4. Run cells sequentially to process images

Each notebook follows a consistent workflow:
- **Configuration Cell**: Set input/output paths and processing parameters
- **Processing/Interactive Cell**: Run main analysis (alignment notebook includes interactive widgets)
- **Export Cell**: Save processed results

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
