import json
from pathlib import Path
from PIL import Image
import argparse
import warnings


def patch_2ds_v2_0_1(data_path : str) -> None:
        
    puzzles = [
        'puzzle_0000031_RP_group_30',
        'puzzle_0000062_RP_group_61',
        'puzzle_0000059_RP_group_58',
    ]

    puzzle_folders = [Path(data_path) / puzzle for puzzle in puzzles]

    for puzzle in puzzle_folders:
        sol_size = Image.open(puzzle / "preview.png").convert('RGBA').size

        data_file = puzzle / "data.json"
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # better we open the file now to lock it for writing
        with open(data_file, "w", encoding="utf-8") as f:
            # Process fragments
            for i, frag in enumerate(data["fragments"]):
                y = frag['pixel_position'][1]
                y = sol_size[1] - y
                data["fragments"][i]['pixel_position'][1] = y
            
            json.dump(data, f, indent=4)
    
   

def main() -> None:

    argparser = argparse.ArgumentParser(description="Process JSON files to adjust fragment positions.")
    argparser.add_argument("input_folder", type=str, help="Path to the folder containing JSON files.")
    args = argparser.parse_args()    

    warnings.warn("This script is not idempotent. Running it multiple times may produce unintended results.", UserWarning)

    warnings.warn("This changes only 'pixel_position' and not 'position'! It should be improved", UserWarning)
    confirm = input("Type 'yes' to continue: \n").strip().lower()
    if confirm != "yes":
        return
    
    print("Continuing...")

    print('Applying v2.0.1 patch..')
    patch_2ds_v2_0_1(args.input_folder)
    print('Patch applied.')



if __name__ == "__main__":
    main()
