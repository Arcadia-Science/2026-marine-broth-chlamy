#!/usr/bin/env python3
"""
Reveal Wisps - Image Stack Processing
======================================
Processes microscopy image stacks to enhance visibility of fine structures
(wisps) using unsharp masking, CLAHE, temporal smoothing, and creates an
annotated side-by-side comparison movie.

Usage:
    python scripts/reveal_wisps.py                        # uses example data
    python scripts/reveal_wisps.py --input my_stack.tif   # custom input
"""

import argparse
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

REPO_ROOT = Path(__file__).resolve().parent.parent

# =============================================================================
# CONFIGURATION — processing parameters (edit as needed)
# =============================================================================

sigma_smooth_background = 2.0
unsharp_amount = 1.5
clahe_clip_limit = 1.5
final_blur_sigma = 0.3
temporal_window = 3

# Annotation parameters
time_per_frame = 0.05868  # seconds
pixel_size = 0.1625  # microns/pixel
scale_bar_microns = 10
scale_bar_height = 5
font_path = "/System/Library/Fonts/SFNSMono.ttf"
font_size = 16


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enhance fine structures (wisps) in microscopy image stacks."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=REPO_ROOT / "data" / "Sample_Wisp_Timelapse.tif",
        help="Path to input TIF stack (default: example data)",
    )
    parser.add_argument(
        "--output-tif",
        type=Path,
        default=None,
        help="Path for processed TIF output (default: output/<stem>_processed.tif)",
    )
    parser.add_argument(
        "--output-movie",
        type=Path,
        default=None,
        help="Path for annotated MP4 movie (default: output/<stem>_movie.mp4)",
    )
    args = parser.parse_args()

    input_file = args.input
    output_dir = REPO_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_file.stem
    output_tif = args.output_tif or output_dir / f"{stem}_processed.tif"
    output_movie = args.output_movie or output_dir / f"{stem}_movie.mp4"
    output_tif.parent.mkdir(parents=True, exist_ok=True)
    output_movie.parent.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # LOAD AND PROCESS
    # =========================================================================

    stack = tifffile.imread(input_file)
    print(f"Loaded stack shape: {stack.shape} dtype: {stack.dtype}")
    n_frames, height, width = stack.shape

    processed_frames = []
    for i in range(n_frames):
        img16 = stack[i]
        img = cv2.normalize(img16, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        background = gaussian_filter(img, sigma=sigma_smooth_background)
        img_unsharp = cv2.addWeighted(img, 1 + unsharp_amount, background, -unsharp_amount, 0)
        clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=(8, 8))
        img_clahe = clahe.apply(img_unsharp)
        processed_frames.append(img_clahe)

    processed_stack = np.stack(processed_frames, axis=0)

    # Temporal smoothing
    pad_w = temporal_window // 2
    padded = np.pad(processed_stack, ((pad_w, pad_w), (0, 0), (0, 0)), mode="edge")
    smoothed_stack = np.empty_like(processed_stack)
    for i in range(n_frames):
        smoothed_stack[i] = np.mean(padded[i : i + temporal_window], axis=0)

    # Final smoothing
    final_stack = np.empty_like(smoothed_stack)
    for i in range(n_frames):
        final_stack[i] = gaussian_filter(smoothed_stack[i], sigma=final_blur_sigma)

    tifffile.imwrite(output_tif, final_stack.astype(np.uint8))
    print(f"Processed TIFF saved to: {output_tif}")

    # =========================================================================
    # CREATE ANNOTATED MOVIE
    # =========================================================================

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        print("Custom font not found, using default")
        font = ImageFont.load_default()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = int(1 / time_per_frame)
    out = cv2.VideoWriter(str(output_movie), fourcc, fps, (2 * width, height), isColor=False)
    scale_bar_length_pixels = int(scale_bar_microns / pixel_size)

    for i in range(n_frames):
        original_norm = cv2.normalize(stack[i], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        processed_frame = final_stack[i].astype(np.uint8)
        combined = np.hstack((original_norm, processed_frame))

        pil_img = Image.fromarray(combined)
        draw = ImageDraw.Draw(pil_img)

        timestamp_text = f"Time: {i * time_per_frame:.2f} s"
        draw.text((10, 10), timestamp_text, font=font, fill=255)

        scale_bar_x = combined.shape[1] - scale_bar_length_pixels - 20
        scale_bar_y = combined.shape[0] - 30
        draw.rectangle(
            [
                scale_bar_x,
                scale_bar_y,
                scale_bar_x + scale_bar_length_pixels,
                scale_bar_y + scale_bar_height,
            ],
            fill=255,
        )
        draw.text(
            (scale_bar_x, scale_bar_y - 20), f"{scale_bar_microns} \u00b5m", font=font, fill=255
        )

        frame_with_text = np.array(pil_img)
        out.write(frame_with_text)

    out.release()
    print(f"Annotated movie saved to: {output_movie}")

    # =========================================================================
    # SHOW SAMPLE
    # =========================================================================

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(stack[n_frames // 2], cmap="gray")
    plt.title("Original Frame")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(final_stack[n_frames // 2], cmap="gray")
    plt.title("Final Processed Frame")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    main()
