import json
from pathlib import Path
from tqdm import tqdm
import argparse


def patch_v2_0_2(data_path : str) -> None:

    puzzle_folders = [p for p in Path(data_path).iterdir() if p.is_dir() and p.name.startswith("puzzle_")]

    for puzzle in tqdm(puzzle_folders):
        data_file = puzzle / "data.json"

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # better we open the file now to lock it for writing
        with open(data_file, "w", encoding="utf-8") as f:
            for i, frag in enumerate(data["fragments"]):
                if 'filename' in frag:
                    data["fragments"][i]['filename'] = frag['filename'].replace('.obj', '.png')

            json.dump(data, f, indent=4)
    
   

def main() -> None:

    argparser = argparse.ArgumentParser(description="Process JSON files to adjust fragment filenames.")
    argparser.add_argument("input_folder", type=str, help="Path to the folder containing JSON files.")
    args = argparser.parse_args()    
    
    print("Continuing...")

    print('Applying v2.0.2 patch..')
    patch_v2_0_2(args.input_folder)
    print('Patch applied.')



if __name__ == "__main__":
    main()
