#!/usr/bin/env python3
"""
Flat-Field Correction for Uneven Illumination
=============================================
Corrects spatial gradients from uneven illumination (e.g., LED light engines like Lida)
by dividing each channel by its blurred version.

Usage:
    1. Set input_dir to folder containing your images
    2. Configure normalization strategy based on your image type:
       - preserve_color_balance=True for RGB brightfield images
       - preserve_color_balance=False for multi-channel fluorescence
    3. Adjust blur_sigma if needed (larger = gentler correction)
    4. Run: python smoothen_lida_rgb_tifs.py
"""

from pathlib import Path

import numpy as np
import tifffile
from scipy.ndimage import gaussian_filter

# =============================================================================
# CONFIGURATION
# =============================================================================

input_dir = "/path/to/your/image/folder"
output_dir = None  # None = creates "corrected" subfolder in input_dir
file_pattern = "*.tif"

# Correction parameters
blur_sigma = 100  # Larger = gentler correction
clip_percentile = 0.1  # Clip top 0.1% to prevent outliers from skewing normalization

# Normalization strategy
preserve_color_balance = True  # True: RGB photos | False: fluorescence multi-channel

# =============================================================================
# PROCESSING FUNCTIONS
# =============================================================================


def correct_channel(
    channel: np.ndarray,
    sigma: float,
    clip_percentile: float,
    norm_factor: float | None = None,
) -> np.ndarray:
    """
    Flat-field correct a single channel by dividing by its blurred version.

    Args:
        channel: Input 2D channel array
        sigma: Gaussian blur sigma for background estimation
        clip_percentile: Percentile to clip (prevents outliers from affecting normalization)
        norm_factor: Pre-computed normalization factor. If None, calculates per-channel.

    Returns:
        Corrected channel normalized to [0, 1] range
    """
    channel_float = channel.astype(np.float64)
    background = gaussian_filter(channel_float, sigma=sigma)
    background = np.clip(background, 1e-10, None)  # Protect against division by zero

    corrected = channel_float / background

    # Normalize to [0, 1]
    if norm_factor is None:
        norm_factor = np.percentile(corrected, 100 - clip_percentile)

    if norm_factor > 1e-10:
        corrected = corrected / norm_factor

    return np.clip(corrected, 0, 1)


def correct_image(
    img: np.ndarray,
    sigma: float,
    clip_percentile: float,
    preserve_color_balance: bool,
) -> np.ndarray:
    """
    Apply flat-field correction to an image.

    Args:
        img: Input image (grayscale, RGB, or multi-channel)
        sigma: Gaussian blur sigma for background estimation
        clip_percentile: Percentile to clip for normalization
        preserve_color_balance: If True, use global normalization for RGB images.
            If False, normalize each channel independently.

    Returns:
        Corrected image as float array in [0, 1] range
    """
    if img.ndim == 2:
        return correct_channel(img, sigma, clip_percentile)

    if img.ndim != 3:
        raise ValueError(f"Unexpected image shape: {img.shape}")

    # Determine channel layout: HWC if last dim is 3-4, otherwise CHW
    if img.shape[2] in [3, 4]:
        channel_axis = 2
        n_channels = img.shape[2]
        is_rgb = True
    else:
        channel_axis = 0
        n_channels = img.shape[0]
        is_rgb = n_channels in [3, 4] and img.shape[0] < img.shape[1]

    # Calculate global normalization factor if preserving color balance
    norm_factor = None
    if preserve_color_balance and is_rgb:
        all_corrected = []
        for c in range(n_channels):
            channel = img[:, :, c] if channel_axis == 2 else img[c]
            ch_float = channel.astype(np.float64)
            bg = gaussian_filter(ch_float, sigma=sigma)
            bg = np.clip(bg, 1e-10, None)
            all_corrected.append(ch_float / bg)
        norm_factor = float(np.percentile(all_corrected, 100 - clip_percentile))

    # Process each channel
    corrected = np.zeros_like(img, dtype=np.float64)
    for c in range(n_channels):
        channel = img[:, :, c] if channel_axis == 2 else img[c]
        result = correct_channel(channel, sigma, clip_percentile, norm_factor)
        if channel_axis == 2:
            corrected[:, :, c] = result
        else:
            corrected[c] = result

    return corrected


def process_file(
    input_path: Path,
    output_path: Path,
    sigma: float,
    clip_percentile: float,
    preserve_color_balance: bool,
) -> None:
    """
    Load, correct, and save a single image file.

    Args:
        input_path: Path to input image
        output_path: Path to save corrected image
        sigma: Gaussian blur sigma
        clip_percentile: Percentile to clip
        preserve_color_balance: Normalization strategy
    """
    print(f"  Processing: {input_path.name}")
    img = tifffile.imread(input_path)
    original_dtype = img.dtype
    print(f"    Shape: {img.shape}, dtype: {original_dtype}")

    corrected = correct_image(img, sigma, clip_percentile, preserve_color_balance)

    # Convert back to original dtype
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


def main() -> None:
    """Main processing loop."""
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
    print(f"Clip percentile: {clip_percentile}%")
    print(f"Preserve color balance: {preserve_color_balance}")
    print(f"Output directory: {output_path}")
    print("-" * 50)

    for f in files:
        out_file = output_path / f"{f.stem}_corrected{f.suffix}"
        try:
            process_file(
                f,
                out_file,
                sigma=blur_sigma,
                clip_percentile=clip_percentile,
                preserve_color_balance=preserve_color_balance,
            )
        except Exception as e:
            print(f"  ERROR processing {f.name}: {e}")

    print("-" * 50)
    print(f"Done! {len(files)} files processed.")


if __name__ == "__main__":
    main()
