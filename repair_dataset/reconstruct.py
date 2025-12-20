from PIL import Image
import math
from .utils import centroid_rgba

def _reassemble_solution_2d(images, positions, solution_size):

    solution_pil = Image.new("RGBA", solution_size, (0, 0, 0, 0))

    for img_pil, pos in zip(images, positions):
        x,y,angle = pos
        
        # pixel_position refers to the position of the centroids, but we want the position of the images
        x_c,y_c = centroid_rgba(img_pil)
        print(img_pil.width//2 - x_c, img_pil.height//2 - y_c)
        x_ = int(x - x_c)
        y_ = int(y - y_c)
        if angle != 0.0:
            img_pil = img_pil.rotate(angle)
        
        solution_pil.paste(img_pil, (x_, y_), img_pil)

    mask = solution_pil.split()[-1]

    return solution_pil.crop(mask.getbbox())
     

def reassemble_2d(solved_fragements, position_key='position_2d', solution_size=None):
    # Determine canvas size
    max_x, max_y = 0, 0
    images = []
    positions = []
    for frag in solved_fragements:
        img_pil = frag['image']
        images.append(img_pil)
        
        x,y, angle = frag[position_key]
        positions.append((x,y,angle))
        
        if solution_size is not None:
            continue
        max_x = int(math.ceil(max(max_x, x + img_pil.width)))
        max_y = int(math.ceil(max(max_y, y + img_pil.height)))

    if solution_size is None:
        solution_size = (max_x, max_y)

    return _reassemble_solution_2d(images, positions, solution_size)