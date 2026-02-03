#!/usr/bin/env python3
"""
Reveal Wisps - Image Stack Processing
======================================
Processes microscopy image stacks to enhance visibility of fine structures
(wisps) using unsharp masking, CLAHE, temporal smoothing, and creates an
annotated side-by-side comparison movie.

Usage:
    1. Set input_file, output_tif, and output_movie paths
    2. Adjust processing parameters as needed
    3. Run script: python reveal_wisps.py
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

# =============================================================================
# CONFIGURATION
# =============================================================================

input_file = "/path/to/your/input_stack.tif"
output_tif = "/path/to/your/output_processed.tif"
output_movie = "/path/to/your/output_movie.mp4"

# Processing parameters
sigma_smooth_background = 2.0
unsharp_amount = 1.5
clahe_clip_limit = 1.5
final_blur_sigma = 0.3
temporal_window = 3

# Annotation parameters
time_per_frame = 0.05868  # seconds
pixel_size = 0.1625       # microns/pixel
scale_bar_microns = 10
scale_bar_height = 5
font_path = "/System/Library/Fonts/SFNSMono.ttf"  # Update for your system
font_size = 16

# =============================================================================
# LOAD AND PROCESS
# =============================================================================

stack = tifffile.imread(input_file)
print(f"Loaded stack shape: {stack.shape} dtype: {stack.dtype}")
n_frames, height, width = stack.shape

processed_frames = []
for i in range(n_frames):
    img16 = stack[i]
    img = cv2.normalize(img16, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    background = gaussian_filter(img, sigma=sigma_smooth_background)
    img_unsharp = cv2.addWeighted(img, 1 + unsharp_amount, background, -unsharp_amount, 0)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=(8,8))
    img_clahe = clahe.apply(img_unsharp)
    processed_frames.append(img_clahe)

processed_stack = np.stack(processed_frames, axis=0)

# Temporal smoothing
pad_width = temporal_window // 2
padded = np.pad(processed_stack, ((pad_width, pad_width), (0, 0), (0, 0)), mode='edge')
smoothed_stack = np.empty_like(processed_stack)
for i in range(n_frames):
    smoothed_stack[i] = np.mean(padded[i:i+temporal_window], axis=0)

# Final smoothing
final_stack = np.empty_like(smoothed_stack)
for i in range(n_frames):
    final_stack[i] = gaussian_filter(smoothed_stack[i], sigma=final_blur_sigma)

tifffile.imwrite(output_tif, final_stack.astype(np.uint8))
print(f"✅ Processed TIFF saved to: {output_tif}")

# =============================================================================
# CREATE ANNOTATED MOVIE
# =============================================================================

try:
    font = ImageFont.truetype(font_path, font_size)
except:
    print("⚠️ Custom font not found, using default")
    font = ImageFont.load_default()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = int(1 / time_per_frame)
out = cv2.VideoWriter(output_movie, fourcc, fps, (2*width, height), isColor=False)
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
    draw.rectangle([scale_bar_x, scale_bar_y,
                   scale_bar_x + scale_bar_length_pixels,
                   scale_bar_y + scale_bar_height], fill=255)
    draw.text((scale_bar_x, scale_bar_y - 20), f"{scale_bar_microns} µm", font=font, fill=255)

    frame_with_text = np.array(pil_img)
    out.write(frame_with_text)

out.release()
print(f"🎬 Annotated movie saved to: {output_movie}")

# =============================================================================
# SHOW SAMPLE
# =============================================================================

plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
plt.imshow(stack[n_frames//2], cmap='gray')
plt.title('Original Frame')
plt.axis('off')

plt.subplot(1,2,2)
plt.imshow(final_stack[n_frames//2], cmap='gray')
plt.title('Final Processed Frame')
plt.axis('off')
plt.show()
