from typing import Union
from pathlib import Path
import random
import json
import warnings

from PIL import Image

from ..utils import center_and_pad_rgba, centroid_rgba, concat_pil_img


def getmetadata_2dsolved(puzzle_folder: Union[str, Path]) -> dict:
    puzzle_folder = Path(puzzle_folder)
    json_path = puzzle_folder / "data.json"
    with open(json_path, 'r') as f:
        data = json.load(f)

    data['path'] = str(puzzle_folder)

    return data

def getitem_2dsolved(puzzle_folder : Union[str,Path], supervised_mode : bool, load_images : bool, apply_random_rotations: bool = False) -> Union[dict, tuple]:

    if apply_random_rotations and not (supervised_mode and load_images):
        raise RuntimeError("Random rotations can only be applied in supervised mode with load_images=True.")

    data = getmetadata_2dsolved(puzzle_folder)

    puzzle_folder = Path(puzzle_folder)
    puzzle_name = puzzle_folder.name

    data['name'] = puzzle_name
    del data['metadata_version']

    for i,frag in enumerate(data['fragments']):
        img_name = Path(frag['filename'])
        del data['fragments'][i]['filename']

        if 'name' not in data['fragments'][i]:
            data['fragments'][i]['name'] = img_name.stem

        #frag_name = data['fragments'][i]['name'] 
        #data['fragments'][i]['full_name'] = f'{puzzle_name}/{frag_name}'
        data['fragments'][i]['image_path'] = str((puzzle_folder / img_name).absolute())

    if not supervised_mode:
        return data
    
    ######## SUPERVISED MODE ########
    
    # in this case supervised_mode is True
    # we split input and target
    # x contains in-memory images and few metadata
    # data contains the original metadata dict with the GT



    fragments = []
    for i, frag in enumerate(data['fragments']):

        frag_ = {key: frag[key] for key in ['idx','name','image_path']}

        if load_images:
            image = Image.open(frag['image_path']).convert('RGBA')
            image = center_and_pad_rgba(image)


            if apply_random_rotations:
                angle = round(random.uniform(0, 359),2)
                angle_orig = frag['position_2d'][2]
                new_angle = (angle_orig + angle) % 360.0


                if angle_orig != 0.0:
                    warnings.warn(f"Fragment {frag} already has a non-zero angle {angle_orig}. Adding random rotation of {angle} on top of it. Resulting angle: {new_angle}")
                
                data['fragments'][i]['position_2d'][2] = new_angle
                image = image.rotate(-angle)

            frag_['image'] = image


        fragments.append(frag_)
    
    x = {
        'name': puzzle_name,
        'fragments': fragments,
    }


    return x, data