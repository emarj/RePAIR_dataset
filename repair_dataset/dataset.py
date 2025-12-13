from pathlib import Path
import json

from typing import Union

from .patches.patch_v3_beta import patch_v3_beta
from .patches.patch_v2_0_1 import patch_v2_0_1
from .patches.patch_v2_0_2 import patch_v2_0_2

from .splits.splits import train_split, test_split

from .manager import DataManager

DEFAULT_VERSION = 'v2.0.1'
SUPPORTED_VERSIONS = ['v2', 'v2.0.1', 'v2.0.2', 'v3-beta']


class RePAIRDataset:
    """Dataset access class for RePAIR puzzles.

    Usage
    - Instantiate with the dataset root (or let DataManager manage extraction by setting managed_mode=True).
    - Index by integer or puzzle name (string) to obtain the puzzle metadata (and images if supervised_mode=True).
    - Use as an iterator to walk puzzles in the active split.

    Parameters
    - root (str or Path): path to the dataset root folder. In manaeged mode, this is where data will be downloaded/extracted.
    - version (str): dataset version. Supported versions are: 'v2', 'v2.0.1', 'v2.0.2', 'v3-beta'.
    - split (None|'train'|'test'): optional dataset split.
    - supervised_mode (bool): if False (default) __getitem__ returns parsed metadata dict.
                              if True, __getitem__ returns a tuple (x, data) where `x` contains
                              in-memory PIL Images for fragments and `data` is the original metadata dict.
                              - x: {'name': <puzzle_name>, 'fragments': [{'idx': int, 'name': str, 'image': PIL.Image}, ...]}
                              - data: original parsed JSON as a dict (with 'path' and 'name' injected for v2 variants).
    - managed_mode (bool): if True the DataManager will be used to ensure data is present and patched.
    - from_scratch (bool): passed to DataManager to force a fresh extraction.
    - skip_verify (bool): passed to DataManager to skip integrity checks.

    Behavior & Notes
    - The loader expects each puzzle to reside in a folder named 'puzzle_<id>' with a data.json file.
    - For v2 series, fragment filenames in the JSON may be .obj while on-disk images are .png; supervised_mode handles this `.obj`->`.png` mapping.
    - When managed_mode=True the constructor may raise on missing or corrupted data; when unmanaged and no data found a RuntimeError is raised.
    - Supports iteration protocol (__iter__/__next__), __len__, and __getitem__ with int or str keys.
    """

    def __init__(self,
                 root,
                 version="",
                 split=None,
                 supervised_mode=False,
                 managed_mode=True,
                 from_scratch=False,
                 skip_verify=False) -> None:
        
        
        self.root = Path(root)
        
        self.split = split
        self.supervised_mode = supervised_mode

        # iterator state
        self._iter_idx = 0
        
        self.version = version
        if self.version == "" or self.version is None:
            if managed_mode:
                # if we manage the data, we set the default version
                self.version = DEFAULT_VERSION
            else:
                raise RuntimeError("When managed_mode is False, version must be specified.")
            
        if version not in SUPPORTED_VERSIONS:
            raise RuntimeError(f"Unsupported dataset version {version}. Supported versions are: {SUPPORTED_VERSIONS}")
        
        if managed_mode:
            patch_map = {
            'v2.0.1': [patch_v2_0_1],
            'v2.0.2': [patch_v2_0_1, patch_v2_0_2],
            'v3-beta': [patch_v3_beta],
            }

            self.datamanager = DataManager(
                root=self.root,
                version=version,
                from_scratch=from_scratch,
                skip_verify=skip_verify,
                patch_map=patch_map,
            )

        ################### Load dataset ###################

        self.data_path = self.datamanager.data_path if managed_mode else self.root
    
        self.puzzle_folders_list = [p for p in self.data_path.iterdir() if p.is_dir() and p.name.startswith("puzzle_")]

        self._make_split()

        if len(self) == 0:
            if managed_mode:
                raise RuntimeError("No data found after extraction. The dataset may be corrupted.")
            else:
                raise RuntimeError("No data found in the specified root folder.")
    
    def _make_split(self) -> None:
        if self.split is None:
            return
        
        if self.split == 'train':
            split = train_split
        elif self.split == 'test':
            split = test_split
        else:
            raise RuntimeError(f"Unsupported split name: {self.split}. Supported splits are: 'train', 'test'")
        
        self._filter(split)

    def _filter(self, filter_list) -> None:

        if filter_list is not None and len(filter_list) > 0:
            self.puzzle_folders_list = [p for p in self.puzzle_folders_list if p.name in filter_list]
        
        # sort because why not
        self.puzzle_folders_list.sort()

        # after the split, use a dict to map string to index for faster access by name
        self.puzzle_folders_map = {p.name: k for k,p in enumerate(self.puzzle_folders_list)}

    # iterator protocol
    def __iter__(self) -> 'RePAIRDataset':
        self._iter_idx = 0
        return self

    def __next__(self) -> Union[dict, tuple]:
        if self._iter_idx >= len(self):
            raise StopIteration
        item = self[self._iter_idx]
        self._iter_idx += 1
        return item
    
    def __len__(self) -> int:
        return len(self.puzzle_folders_list)

    def __getitem__(self, key : Union[int, str]) -> Union[dict, tuple]:

        if isinstance(key, int):
            puzzle_folder = self.puzzle_folders_list[key]
        elif isinstance(key, str):
            puzzle_folder = self.puzzle_folders_list[self.puzzle_folders_map[key]]
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
        
        json_path = puzzle_folder / "data.json"

        puzzle_name = puzzle_folder.name

        with open(json_path, 'r') as f:
            data = json.load(f)
        
        if self.version.startswith('v2'):
            # add names
            data['name'] = puzzle_name
            for i,frag in enumerate(data['fragments']):
                frag_name = Path(frag['filename']).stem
                data['fragments'][i]['name'] = frag_name
            
        # add path in any case
        data['path'] = str(puzzle_folder)

        if not self.supervised_mode:
            return data
        
        # in this case self.supervised_mode is True
        # we return images inside the dataset object
        from PIL import Image

        fragments = []
        for frag in data['fragments']:
            # in v2, filenames are .obj, we need to load .png
            image_path = puzzle_folder / frag['filename'].replace('.obj', '.png')
            image = Image.open(image_path).convert('RGBA')

            frag_dict = {
                'idx': frag['idx'],
                'name': frag.get('name', Path(frag['filename']).stem),
                'image': image,
            }
            fragments.append(frag_dict)
        
        x = {
            'name': puzzle_name,
            'fragments': fragments,
        }


        return x, data
