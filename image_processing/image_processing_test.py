#!/usr/bin/env python3
"""
Image Processing Test Program
Based on learning from: Python 3 Image Processing - Ashwin Pajankar

Demonstrates:
- Loading images with PIL
- Converting to grayscale using NumPy
- Simple thresholding
- Basic image statistics
"""

import numpy as np
from PIL import Image
import os

def load_image(path):
    """Load an image and return as PIL Image."""
    if not os.path.exists(path):
        # Create a test pattern if image doesn't exist
        print(f"Creating test pattern (no image found at {path})")
        return create_test_pattern()
    return Image.open(path)

def create_test_pattern(width=200, height=200):
    """Create a simple test pattern with gradients and shapes."""
    # Create RGB image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient (left to right: dark to light)
    for i in range(width):
        img[:, i] = [i, i, i]
    
    # Add some colored rectangles
    img[20:60, 20:60] = [255, 0, 0]    # Red square
    img[80:120, 80:120] = [0, 255, 0]  # Green square
    img[140:180, 20:60] = [0, 0, 255]  # Blue rectangle
    
    return Image.fromarray(img)

def rgb_to_grayscale(pil_img):
    """Convert RGB image to grayscale using NumPy."""
    # Convert to numpy array
    img_array = np.array(pil_img)
    
    # Get dimensions
    if len(img_array.shape) == 3:
        # RGB to grayscale: weighted average (luminosity method)
        # Y = 0.299R + 0.587G + 0.114B
        gray = 0.299 * img_array[:, :, 0] + \
               0.587 * img_array[:, :, 1] + \
               0.114 * img_array[:, :, 2]
        return gray.astype(np.uint8)
    return img_array

def apply_threshold(gray_img, threshold=128):
    """Apply simple binary thresholding."""
    img_array = np.array(gray_img)
    binary = img_array > threshold
    # Return as uint8 (0 or 255)
    return (binary * 255).astype(np.uint8)

def compute_histogram(gray_img):
    """Compute image histogram using NumPy."""
    img_array = np.array(gray_img).flatten()
    hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
    return hist

def get_image_stats(gray_img):
    """Get basic statistics of grayscale image."""
    img_array = np.array(gray_img)
    return {
        'shape': img_array.shape,
        'min': img_array.min(),
        'max': img_array.max(),
        'mean': img_array.mean(),
        'std': img_array.std()
    }

def main():
    # Load or create test image
    test_image_path = "/media/tony/Drive2/Programs/test_input.png"
    
    # Try to find an actual image, otherwise use test pattern
    sample_images = [
        "/media/tony/Pictures/sample.png",
        "/home/tony/Pictures/test.png"
    ]
    
    pil_img = None
    for path in sample_images:
        if os.path.exists(path):
            pil_img = Image.open(path)
            break
    
    if pil_img is None:
        pil_img = create_test_pattern()
    
    print(f"Original image mode: {pil_img.mode}, size: {pil_img.size}")
    
    # Convert to grayscale
    gray_img = rgb_to_grayscale(pil_img)
    print(f"Grayscale shape: {gray_img.shape}")
    
    # Apply thresholding
    threshold = 128
    binary_img = apply_threshold(gray_img, threshold)
    print(f"Binary threshold applied: {threshold}")
    
    # Compute statistics
    stats = get_image_stats(gray_img)
    print(f"\nImage Statistics:")
    for k, v in stats.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
    
    # Compute histogram
    hist = compute_histogram(gray_img)
    print(f"\nHistogram (top 5 bins): {hist[:5]}")
    print(f"Histogram (bottom 5 bins): {hist[-5:]}")
    
    # Save results
    gray_pil = Image.fromarray(gray_img)
    gray_pil.save("/media/tony/Drive2/Programs/grayscale_output.png")
    
    binary_pil = Image.fromarray(binary_img)
    binary_pil.save("/media/tony/Drive2/Programs/binary_output.png")
    
    print("\nSaved outputs:")
    print("  - grayscale_output.png")
    print("  - binary_output.png")

if __name__ == "__main__":
    main()
