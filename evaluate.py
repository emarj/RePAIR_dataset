import argparse
from pathlib import Path

from tqdm import tqdm

import numpy as np
from PIL import Image

from repair_dataset import RePAIRDataset
from repair_dataset.utils import centroid_rgba


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




def evaluate_gt(dataset_path,
                managed_mode=True,
                filter=None,
                version=None,
                from_scratch=False,
                save_images=False):
    
    if filter is None:
        filter = []

    print('Loading dataset...')
    dataset = RePAIRDataset(dataset_path,
                            version=version,
                            managed_mode=managed_mode,
                            from_scratch=from_scratch)
    dataset._filter(filter)
    print(f"Found {len(dataset)} puzzles")

    name = f"eval_gt_{dataset.version_type}"
    base_path = Path(dataset_path) / name
    csv_path = Path(dataset_path) / f"{name}.csv"

    if save_images:
        base_path.mkdir(parents=True, exist_ok=True)

    deltas = [-1] * len(dataset)

    with open(csv_path, "w", buffering=1) as f:
        f.write('PuzzleName Difference\n')

        for i, data in enumerate(tqdm(dataset, desc="Evaluating puzzles")):
            if len(filter) > 0 and data['name'] not in filter:
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
    
    parser = argparse.ArgumentParser(description="Evaluate RePAIR dataset against ground truth images")
    parser.add_argument('--dataset_path', default=".dataset/RePAIR", help="Path to dataset")
    parser.add_argument('--filter', nargs='*', help='List of puzzle names to include')
    parser.add_argument('--version', required=True, help='Dataset version')
    parser.add_argument('--save-images', action='store_true', default=False, help='Save solution and diff images')
    parser.add_argument('--no-managed-mode', dest='managed_mode', action='store_false', help='Do not use managed_mode dataset')
    parser.add_argument('--from-scratch', dest='from_scratch', action='store_true', help='Force fresh extraction (only in managed mode)')
    args = parser.parse_args()

    evaluate_gt(args.dataset_path,
                managed_mode=args.managed_mode,
                from_scratch=args.from_scratch,
                filter=args.filter,
                version=args.version,
                save_images=args.save_images,
                )




if __name__ == "__main__":
    main()