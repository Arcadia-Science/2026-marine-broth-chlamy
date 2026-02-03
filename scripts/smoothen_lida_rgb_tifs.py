#!/usr/bin/env python3
"""
Batch Flat-Field Correction for Uneven Illumination
====================================================
Corrects color gradients from LED light engines (like Lida) by
dividing each channel by its blurred version.

Usage:
    1. Set input_dir to folder containing your images
    2. Set output_dir (or leave as None to create subfolder)
    3. Adjust blur_sigma if needed (larger = gentler correction)
    4. Run script: python smoothen_lida_rgb_tifs.py
"""

import numpy as np
from pathlib import Path
from skimage import io, img_as_float, img_as_uint, img_as_ubyte
from scipy.ndimage import gaussian_filter
import tifffile

# =============================================================================
# CONFIGURATION
# =============================================================================

input_dir = "/path/to/your/image/folder"
output_dir = None  # None = creates "corrected" subfolder in input_dir
file_pattern = "*.tif"

blur_sigma = 100
clip_percentile = 0.1

# =============================================================================
# PROCESSING FUNCTIONS
# =============================================================================

def correct_channel(channel, sigma=100):
    """Flat-field correct a single channel by dividing by blurred version."""
    channel_float = channel.astype(np.float64)
    background = gaussian_filter(channel_float, sigma=sigma)
    background[background == 0] = 1
    corrected = channel_float / background
    corrected = corrected / np.percentile(corrected, 100 - clip_percentile)
    corrected = np.clip(corrected, 0, 1)
    return corrected


def correct_image(img, sigma=100):
    """Apply flat-field correction to an image (handles grayscale, RGB, or multi-channel)."""
    if img.ndim == 2:
        corrected = correct_channel(img, sigma)
    elif img.ndim == 3:
        if img.shape[2] in [3, 4]:
            corrected = np.zeros_like(img, dtype=np.float64)
            for c in range(img.shape[2]):
                corrected[:, :, c] = correct_channel(img[:, :, c], sigma)
        else:
            corrected = np.zeros_like(img, dtype=np.float64)
            for c in range(img.shape[0]):
                corrected[c] = correct_channel(img[c], sigma)
    else:
        raise ValueError(f"Unexpected image shape: {img.shape}")
    return corrected


def process_file(input_path, output_path, sigma=100):
    """Load, correct, and save a single image."""
    print(f"  Processing: {input_path.name}")
    img = tifffile.imread(input_path)
    original_dtype = img.dtype
    print(f"    Shape: {img.shape}, dtype: {original_dtype}")

    corrected = correct_image(img, sigma)

    if original_dtype == np.uint16:
        corrected_out = (corrected * 65535).astype(np.uint16)
    elif original_dtype == np.uint8:
        corrected_out = (corrected * 255).astype(np.uint8)
    else:
        corrected_out = corrected.astype(np.float32)

    tifffile.imwrite(output_path, corrected_out)
    print(f"    Saved: {output_path.name}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    input_path = Path(input_dir)

    if output_dir is None:
        output_path = input_path / "corrected"
    else:
        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)
    files = sorted(input_path.glob(file_pattern))

    if not files:
        print(f"No files matching '{file_pattern}' found in {input_path}")
        return

    print(f"Found {len(files)} files to process")
    print(f"Blur sigma: {blur_sigma}")
    print(f"Output directory: {output_path}")
    print("-" * 50)

    for f in files:
        out_file = output_path / f"{f.stem}_corrected{f.suffix}"
        try:
            process_file(f, out_file, sigma=blur_sigma)
        except Exception as e:
            print(f"  ERROR processing {f.name}: {e}")

    print("-" * 50)
    print(f"Done! {len(files)} files processed.")


if __name__ == "__main__":
    main()
