from PIL import Image
import numpy as np
from pathlib import Path
from repair_dataset.utils import centroid_rgba
from repair_dataset.dataset import RePAIRDataset
from tqdm import tqdm
import argparse


def save_resized(image, path, downsize_factor=4):
    width, height = image.size
    new_size = (width // downsize_factor, height // downsize_factor)
    image.resize(new_size, Image.LANCZOS).save(str(path))

def evaluate_puzzle(data):

    path = Path(data['path'])
    fragments = data['fragments']

    # gt_folder = output_folder / 'gt'
    # gt_folder.mkdir(parents=True, exist_ok=True)
    # diff_folder = output_folder / 'diff'
    # diff_folder.mkdir(parents=True, exist_ok=True)
    
    gt_path = path / "preview.png"
    gt_pil = Image.open(gt_path).convert('RGBA')


    sol_size = gt_pil.size
    solution_pil = Image.new("RGBA", sol_size, (0, 0, 0, 0))

    position_key = 'pixel_position'
    if position_key not in fragments[0]:
        position_key = 'position_2d'
        if position_key not in fragments[0]:
            raise RuntimeError("Fragment does not contain position key 'pixel_position' nor 'position_2d'")

    for frag in fragments:
        img_path = path / frag['filename'].replace('.obj', '.png')
        img_pil = Image.open(img_path).convert('RGBA')
        img_cropped_pil = img_pil.crop((img_pil.split()[-1]).getbbox())
        
        # pixel_position refers to the position of the centroids, but we want the position of the images
        d_x,d_y = centroid_rgba(img_cropped_pil)
        x = int(frag[position_key][0] - d_x)
        y = int(frag[position_key][1] - d_y)

        solution_pil.paste(img_cropped_pil, (x, y), img_cropped_pil)

    a = np.array(solution_pil.split()[-1])
    b = np.array(gt_pil.split()[-1])

    mask_a = a > 0
    mask_b = b > 0

    mask_ab = mask_a != mask_b

    mask_pil = Image.fromarray((mask_ab * 255).astype(np.uint8), mode='L')

    delta = np.sum(mask_ab) / a.size * 100

    return delta, solution_pil, gt_pil, mask_pil




def evaluate_gt(dataset_path, managed=True, filter = [], version='v2', save_images=False):
    print('Loading dataset...')
    dataset = RePAIRDataset(dataset_path, version=version, supervised_mode=False, managed=managed)
    dataset._filter(filter)
    print(f"Found {len(dataset)} puzzles")

    name = f"eval_gt_{version}"
    base_path = Path(dataset_path) / name

    if save_images:
        base_path.mkdir(parents=True, exist_ok=True)

    

    deltas = [-1] * len(dataset)

    with open(base_path.with_suffix(".csv"), "w", buffering=1) as f:
        f.write('PuzzleName Difference\n')

        for i, data in enumerate(tqdm(dataset, desc="Evaluating puzzles")):
            if len(filter) and data['name'] not in filter:
                continue
            delta, img_sol, gt_pil, delta_img = evaluate_puzzle(data)
            f.write(f"{data['name']} {delta:06.2f}\n")
            deltas[i] = delta
            if save_images:
                save_resized(gt_pil,  base_path / f"{data['name']}_gt.png")
                save_resized(img_sol, base_path / f"{data['name']}_solution.png")
                save_resized(delta_img, base_path / f"{data['name']}_diff.png")

    deltas_np = np.array(deltas, dtype=np.uint8)
    num_invalid = np.sum(deltas_np > 0)

    print(f'Evaluation complete. Results saved to {base_path.with_suffix(".csv")}')
    print(f'Average difference is {deltas_np.mean()}.')
    if num_invalid > 0:
        print(f'WARNING: Found {num_invalid} problems (out of {len(dataset)} puzzles).') 



def main():
    default_filter = [
        'puzzle_0000031_RP_group_30',
        'puzzle_0000062_RP_group_61',
        'puzzle_0000059_RP_group_58',
    ]

    parser = argparse.ArgumentParser(description="Evaluate RePAIR dataset against ground truth images")
    parser.add_argument('dataset_path', nargs='?', default=".dataset/RePAIR_v2", help="Path to dataset")
    parser.add_argument('--managed', dest='managed', action='store_true', help='Use managed dataset', default=True)
    parser.add_argument('--filter', nargs='*', default=default_filter, help='List of puzzle names to include')
    parser.add_argument('--version', default='v2', help='Dataset version')
    parser.add_argument('--save-images', action='store_true', default=False, help='Save solution and diff images')
    args = parser.parse_args()

    evaluate_gt(args.dataset_path, managed=args.managed, filter=args.filter, version=args.version, save_images=args.save_images)



if __name__ == "__main__":
    main()