from typing import Union
from pathlib import Path
import json

from PIL import Image


def getmetadata_2dsolved(puzzle_folder: Union[str, Path]) -> dict:
    puzzle_folder = Path(puzzle_folder)
    json_path = puzzle_folder / "data.json"
    with open(json_path, 'r') as f:
        data = json.load(f)

    data['path'] = str(puzzle_folder)

    return data

def getitem_2dsolved(puzzle_folder : Union[str,Path], supervised_mode : bool) -> Union[dict, tuple]:

    data = getmetadata_2dsolved(puzzle_folder)

    puzzle_folder = Path(puzzle_folder)
    puzzle_name = puzzle_folder.name

    metadata_version = data.get('metadata_version', 2)

    
    if metadata_version == '2':
        # FIXME: why should we do this? If one wants this they should use a patched dataset
        # this was done before patches were implemented
        # removing this would break evaluation script, but maybe the code should be moved there
        data['name'] = puzzle_name
        for i,frag in enumerate(data['fragments']):
            frag_name = Path(frag['filename']).stem
            data['fragments'][i]['name'] = frag_name

    if not supervised_mode:
        return data
    
    ######## SUPERVISED MODE ########
    
    # in this case supervised_mode is True
    # we split input and target
    # x contains in-memory images and few metadata
    # data contains the original metadata dict with the GT


    fragments = []
    for frag in data['fragments']:
        # if version less than v2.0.2, filenames are .obj, we need to load .png
        # TODO: we should check the version properly
        image_path = puzzle_folder / frag['filename'].replace('.obj', '.png')
        image = Image.open(image_path).convert('RGBA')

        fragments.append({
            'idx': frag['idx'],
            'name': frag.get('name', Path(frag['filename']).stem),
            'image': image,
        })
    
    x = {
        'name': puzzle_name,
        'fragments': fragments,
    }


    return x, data