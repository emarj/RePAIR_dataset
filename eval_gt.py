from PIL import Image
import numpy as np
from pathlib import Path
from repair_dataset import RePAIRDataset

def centroid_rgba(img):
    a = np.array(img)[:, :, 3]        # alpha channel
    ys, xs = np.where(a > 0)          # foreground pixels
    return xs.mean(), ys.mean()

def save_resized(image, path, downsize_factor):
    width, height = image.size
    new_size = (width // downsize_factor, height // downsize_factor)
    image.resize(new_size, Image.LANCZOS).save(str(path))

def process(name,fragments,output_folder,downsize_factor=4):

    if isinstance(output_folder, str):
        output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # gt_folder = output_folder / 'gt'
    # gt_folder.mkdir(parents=True, exist_ok=True)
    # diff_folder = output_folder / 'diff'
    # diff_folder.mkdir(parents=True, exist_ok=True)

    gt_folder = output_folder
    diff_folder = output_folder
    
    gt_path = Path(fragments[0]['image_path']).with_name("preview.png")
    gt_pil = Image.open(gt_path).convert('RGBA')
    save_resized(gt_pil, gt_folder / f"{name}_gt.png", downsize_factor)


    sol_size = gt_pil.size
    solution_pil = Image.new("RGBA", sol_size, (0, 0, 0, 0))

    for frag in fragments: 
        img_pil = Image.open(frag['image_path']).convert('RGBA')
        img_cropped_pil = img_pil.crop((img_pil.split()[-1]).getbbox())
        
        # pixel_position refers to the position of the centroids, but we want the position of the images
        d_x,d_y = centroid_rgba(img_cropped_pil)
        x = int(frag['pixel_position'][0] - d_x)
        y = int(frag['pixel_position'][1] - d_y)

        solution_pil.paste(img_cropped_pil, (x, y), img_cropped_pil)

    sol_image_path = gt_folder / f"{name}_solution.png"
    save_resized(solution_pil, sol_image_path, downsize_factor)
    

    a = np.array(solution_pil.split()[-1])
    b = np.array(gt_pil.split()[-1])

    mask_a = a > 0
    mask_b = b > 0

    mask_ab = mask_a != mask_b 

    diff_measure = np.sum(mask_ab) / a.size * 100

    diff_pil = Image.fromarray((mask_ab.astype(np.uint8)) * 255, mode = 'L')
    diff_image_path = diff_folder / f"{name}_diff.png"
    save_resized(diff_pil, diff_image_path, downsize_factor)

    return diff_measure




if __name__ == "__main__":
    print('Loading dataset...')
    dataset = RePAIRDataset(".dataset")
    print(f"Loaded {len(dataset)} puzzles")

    output_folder = Path('.dataset/eval/')
    output_folder.mkdir(parents=True, exist_ok=True)

    with open(output_folder / "log.csv", "w", buffering=1) as f:
        f.write('PuzzleName Difference\n')

        for sample in dataset:
            print(f"Processing puzzle {sample['name']}...")
            diff_measure = process(sample['name'], sample['data']['fragments'],output_folder)
            f.write(f"{sample['name']} {diff_measure:06.2f}\n")
