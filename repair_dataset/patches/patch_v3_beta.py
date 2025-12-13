from PIL import Image
from pathlib import Path
from repair_dataset.utils import centroid_rgba
from tqdm import tqdm
import json
import argparse
import shutil

def patch_v3_beta(dataset_path : str) -> None:
    convert_to_v3(dataset_path, patch_mode=True)

def convert_to_v3(dataset_path,output_path=None,in_place=False,patch_mode=False):

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
  
        output_path = Path(output_path)
        if not in_place and not patch_mode:
            if output_path.exists():
                raise RuntimeError(f"Output path {output_path} already exists, cannot overwrite.")
            output_path.mkdir(parents=True, exist_ok=False)

        # Load folders
        puzzle_folders = sorted([p for p in Path(dataset_path).iterdir() if p.is_dir() and p.name.startswith("puzzle_")])
        
        data = {}

        for puzzle_folder in tqdm(puzzle_folders, desc="Converting to v3-beta"):
            puzzle_name = puzzle_folder.name

            with open(puzzle_folder / 'data.json','r') as f:
                sample = json.load(f)


            data = {
                'name' : puzzle_name,
                'dataset_version' : 'v3-beta',
                'fragments' : [],
                'adjacency': sample['adjacency'],
            }

            new_puzzle_folder = output_path / puzzle_name
            if not in_place:
                new_puzzle_folder.mkdir(parents=True, exist_ok=True)
            
            for frag in sample['fragments']:
                image_path = puzzle_folder / frag['filename'].replace('.obj','.png')
                img_pil = Image.open(image_path).convert('RGBA')

                x,y = centroid_rgba(img_pil)

                if in_place:
                    new_image_path = new_puzzle_folder / (image_path.stem + '_cropped.png')
                else:
                    new_image_path = new_puzzle_folder / image_path.name

                img_cropped_pil = img_pil.crop((img_pil.split()[-1]).getbbox())
                img_cropped_pil.save(new_image_path)
                

                data['fragments'].append({
                    'name' : image_path.stem,
                    'idx': frag['idx'],
                    'filename': str(new_image_path.name),   #.replace('.png','.obj'),
                    'position_2d': [x,y,0.0]
                })


            if not in_place: 
                output_json_path = new_puzzle_folder / 'data.json'
            else:
                output_json_path = new_puzzle_folder / 'data_v3.json'
            
            with open(output_json_path, 'w') as f:
                json.dump(data, f, indent=4)

            if not in_place and not patch_mode:
                # copy preview image
                preview_src = puzzle_folder / 'preview.png'
                preview_dst = new_puzzle_folder / 'preview.png'
                shutil.copy(preview_src, preview_dst)

                adj_preview_src = puzzle_folder / 'adjacency_preview.png'
                adj_preview_dst = new_puzzle_folder / 'adjacency_preview.png'
                shutil.copy(adj_preview_src, adj_preview_dst)
            
            # no need for this because the filename is the same
            # if delete_old:
            #     (puzzle_folder / 'data.json').unlink()  


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Recompute ground truth data.json with cropped images and centroid positions")
    argparser.add_argument('--dataset_path', type=str,required=True, help="Path to RePAIR dataset root folder")
    argparser.add_argument('--output_path', type=str, default=None, help="Path to output folder")
    argparser.add_argument('--in-place', action='store_true',default=False, help="Overwrite data in place")
    args = argparser.parse_args()

    convert_to_v3(args.dataset_path, args.output_path, args.in_place)
