import os
import cairosvg
from PIL import Image
import numpy as np
from tqdm import tqdm

# Path to the CubiCasa high_quality folder containing subfolders (e.g. 19, 337, ...)
SVG_ROOT = r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\high_quality"

# Output folder where we will store the final 512x512 PNGs
OUTPUT_DIR = r"D:\\Documents\\UTBM\\SEM-5\\AI54\\Project\\cubicasa5k\\cubicasa5k\\high_quality_png"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def crop_to_content(img, threshold=10, padding=20):
    """
    Crop image to non-black content with a small padding.

    threshold: pixel values above this (0–255) are considered non-background.
    padding: extra pixels kept around the detected bounding box.
    """
    # Convert to grayscale
    gray = img.convert("L")
    arr = np.array(gray)

    # Non-black mask: True where pixel is not pure background
    mask = arr > threshold
    coords = np.column_stack(np.where(mask))

    # If nothing is found, just return original image
    if coords.size == 0:
        return img

    # coords are (y, x)
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    # Add padding and clamp to image size
    y0 = max(0, y0 - padding)
    x0 = max(0, x0 - padding)
    y1 = min(arr.shape[0], y1 + padding)
    x1 = min(arr.shape[1], x1 + padding)

    return img.crop((x0, y0, x1, y1))


for folder in tqdm(os.listdir(SVG_ROOT)):
    folder_path = os.path.join(SVG_ROOT, folder)
    if not os.path.isdir(folder_path):
        continue

    svg_path = os.path.join(folder_path, "model.svg")
    if not os.path.exists(svg_path):
        continue

    # Temporary large render and final output path
    temp_png = os.path.join(OUTPUT_DIR, f"{folder}_tmp.png")
    final_png = os.path.join(OUTPUT_DIR, f"{folder}.png")

    try:
        # 1) Render SVG at high resolution (big canvas, no crop yet)
        cairosvg.svg2png(
            url=svg_path,
            write_to=temp_png,
            output_width=2048,
            output_height=2048
        )

        # 2) Open and convert to RGB
        img = Image.open(temp_png).convert("RGB")

        # 3) Crop to non-black content with padding
        img = crop_to_content(img, threshold=10, padding=20)

        # 4) Resize cropped region to 512x512
        img = img.resize((512, 512), Image.LANCZOS)

        # 5) Save final image and remove temp
        img.save(final_png)
        os.remove(temp_png)

    except Exception as e:
        print(f"Failed on {folder}: {e}")

print("SVG → cropped 512x512 PNG conversion completed.")
