import random
from typing import Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import argparse
import warnings

from PIL import Image
from tqdm import tqdm

from repair_dataset.utils import align_and_pad_rgba, centroid_rgba

def patch_2ds_v3_b2(dataset_path : str) -> None:
    convert_to_v3_b2(dataset_path, patch_mode=True)

def convert_to_v3_b2(dataset_path : Union[str, Path], output_path : Union[str, Path, None] = None, in_place : bool = False, patch_mode : bool = False) -> None:

        if not patch_mode:
            if in_place and output_path is not None:
                raise RuntimeError("Cannot use in-place and 'output_path' at the same time")
        
            if output_path is None and not in_place:
                raise RuntimeError("Either 'in-place' or 'output_path' must be specified")

        if patch_mode:
            in_place = False
            #delete_old = True

        if in_place or patch_mode:
            output_path = dataset_path
  
        output_path = Path(output_path) # type: ignore
        if not in_place and not patch_mode:
            if output_path.exists():
                raise RuntimeError(f"Output path {output_path} already exists, cannot overwrite.")
            output_path.mkdir(parents=True, exist_ok=False)

        # Load folders
        puzzle_folders = sorted([p for p in Path(dataset_path).iterdir() if p.is_dir() and p.name.startswith("puzzle_")])
        

        def process_directory(puzzle_folder:Path):
            puzzle_name = puzzle_folder.name

            with open(puzzle_folder / 'data.json','r') as f:
                data = json.load(f)

            new_puzzle_folder = output_path / puzzle_name
            if not in_place:
                new_puzzle_folder.mkdir(parents=True, exist_ok=True)

            fragments = data['fragments']
            for i, _ in enumerate(fragments):
                image_path = puzzle_folder / fragments[i]['filename']
                img_pil = Image.open(image_path).convert('RGBA')

                angle = round(random.uniform(0, 359),2)
                if 'position_2d' not in fragments[i]:
                    raise RuntimeError(f"Fragment {fragments[i]} does not have 'position_2d' key required for random rotation.")
                
                x,y, original_angle = fragments[i]['position_2d']
                if original_angle != 0.0:
                    warnings.warn(f"Fragment {fragments[i]} already has a non-zero angle {original_angle}. Adding random rotation on top of it.")
                new_angle = original_angle + angle
                fragments[i]['position_2d'] = (x,y, new_angle)

                x,y = centroid_rgba(img_pil)

                if in_place:
                    new_image_path = new_puzzle_folder / (image_path.stem + '_cropped_padded.png')
                else:
                    new_image_path = new_puzzle_folder / image_path.name

                #img_pil.show()
                img_pil = align_and_pad_rgba(img_pil)
                #img_pil.show()
                img_pil = img_pil.rotate(-new_angle)
                #img_pil.show()
                img_pil.save(new_image_path)

                #breakpoint()
                

            data['fragments'] = fragments


            if not in_place: 
                output_json_path = new_puzzle_folder / 'data.json'
            else:
                output_json_path = new_puzzle_folder / 'data_v3-beta.2.json'
            
            with open(output_json_path, 'w') as f:
                json.dump(data, f, indent=4)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(process_directory, d) for d in puzzle_folders]

            for _ in tqdm(as_completed(futures), total=len(futures),desc="Converting to v3-beta.2"):
                pass

  


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Recompute ground truth data.json with cropped images and centroid positions")
    argparser.add_argument('--dataset_path', type=str,required=True, help="Path to RePAIR dataset root folder")
    argparser.add_argument('--output_path', type=str, default=None, help="Path to output folder")
    argparser.add_argument('--in-place', action='store_true',default=False, help="Overwrite data in place")
    args = argparser.parse_args()

    convert_to_v3_b2(args.dataset_path, args.output_path, args.in_place)
