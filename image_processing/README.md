# Image Processing Test Program

A Python-based image processing demonstration program using PIL and NumPy.

## What It Does

- Loads images using PIL (Python Imaging Library)
- Converts RGB images to grayscale using NumPy
- Applies binary thresholding to grayscale images
- Computes image histograms and basic statistics (min, max, mean, std)
- Creates test patterns if no input image is provided

## How to Run

```bash
cd /media/tony/Drive2/Programs/image_processing
python image_processing_test.py
```

The program will:
1. Look for test images in common locations (`/media/tony/Pictures/sample.png`, `/home/tony/Pictures/test.png`)
2. If no image is found, create a test pattern with gradients and colored rectangles
3. Process the image and save outputs to `/media/tony/Drive2/Programs/`

## Requirements

- Python 3.x
- NumPy (`pip install numpy`)
- Pillow (`pip install Pillow`)

## Output Files

- `grayscale_output.png` - Grayscale version of the input image
- `binary_output.png` - Binary (thresholded) version of the image
