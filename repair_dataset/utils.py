from typing import Tuple
import math
import warnings

import numpy as np
from PIL import Image, ImageDraw, ImageFont

def centroid_rgba(img) -> Tuple[float, float]:
    a = np.array(img)[:, :, 3]        # alpha channel
    ys, xs = np.where(a > 0)          # foreground pixels
    if len(xs) == 0:                  # handle empty / fully transparent images
        raise ValueError("Image has no foreground pixels")
    cx = round(xs.mean(),2)
    cy = round(ys.mean(),2)
    return cx, cy

def concat_pil_img(images, axis=0) -> Image.Image:
    """Concatenate a list of PIL images along the specified axis (0 for vertical, 1 for horizontal)."""
    widths, heights = zip(*(i.size for i in images))

    if axis == 0:  # vertical
        total_height = sum(heights)
        max_width = max(widths)
        new_im = Image.new('RGBA', (max_width, total_height))

        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]
    else:  # horizontal
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new('RGBA', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

    return new_im

def create_image_grid(data, grid_size=None, padding=10, font_size=20):
    """
    Create a grid image from a list of dictionaries containing 'name' and 'image'.
    
    Args:
        data (list of dict): Each dict must have keys 'name' (str) and 'image' (PIL.Image).
        grid_size (tuple, optional): (cols, rows). If None, calculate a square-ish grid.
        padding (int): Space between images.
        font_size (int): Font size for the names.
        
    Returns:
        PIL.Image: The resulting grid image.
    """
    
    if not data:
        raise ValueError("Data list is empty")
    
    # Determine grid size
    n = len(data)
    if grid_size is None:
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
    else:
        cols, rows = grid_size
    
    # Determine max image width and height
    max_width = max(img_dict['image'].width for img_dict in data)
    max_height = max(img_dict['image'].height for img_dict in data)
    
    # Load a default font
    font = ImageFont.load_default()
    
    # Determine height for text
    text_height = max(font.getbbox(img_dict['name'])[3] for img_dict in data)
    
    # Create a blank canvas
    grid_width = cols * max_width + (cols + 1) * padding
    grid_height = rows * (max_height + text_height) + (rows + 1) * padding
    grid_image = Image.new("RGBA", (grid_width, grid_height), color=(0, 0, 0, 0))
    
    # Draw each image and name
    draw = ImageDraw.Draw(grid_image)
    for idx, img_dict in enumerate(data):
        col = idx % cols
        row = idx // cols
        x = padding + col * (max_width + padding)
        y = padding + row * (max_height + text_height + padding)
        
        # Draw the name centered above the image
        text = img_dict['name']
        text_width = font.getbbox(text)[2]
        text_x = x + (max_width - text_width) // 2
        text_y = y
        draw.text((text_x, text_y), text, fill="black", font=font)
        
        # Paste the image below the text
        img_y = y + text_height
        grid_image.paste(img_dict['image'], (x, img_y))
    
    return grid_image

def center_and_pad_rgba(img: Image.Image) -> Image.Image:
    # --- 1. Tight bbox using PIL ---
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("Empty image")

    cropped = img.crop(bbox)

    # --- 2. Get opaque pixel coordinates ---
    a = np.array(cropped.split()[-1], dtype=np.float32)
    ys, xs = np.nonzero(a > 0)

    # --- 3. Centroid (alpha-weighted optional) ---
    weights = a[ys, xs]
    cx = np.average(xs, weights=weights)
    cy = np.average(ys, weights=weights)

    # --- 4. MAX DISTANCE ---
    dx = xs - cx
    dy = ys - cy
    r = np.sqrt(dx*dx + dy*dy).max()

    # --- 5. Canvas size from that radius ---
    size = 2 * int(np.ceil(r)) + 1  # make it odd

    # --- 6. Integer placement ---
    C = (size - 1) / 2
    tx = int(np.floor(C - cx))
    ty = int(np.floor(C - cy))

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(cropped, (tx, ty), cropped)

    return canvas
