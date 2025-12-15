from pathlib import Path
import json
from typing import Union, Tuple

from PIL import Image

from .splits.splits import train_split, test_split

from .manager import DataManager
from .version_type import VersionType

from .data import (
    DEFAULT_VERSION,
    DEFAULT_TYPE,
    SUPPORTED_VERSIONS_TYPES,
    PATCH_MAP,
    REMOTES,
)


class RePAIRDataset:
    """Dataset access class for RePAIR puzzles.

    Usage
    - Instantiate with the dataset root (or let DataManager manage extraction by setting managed_mode=True).
    - Index by integer or puzzle name (string) to obtain the puzzle metadata (and images if managed_mode=True).
    - Use as an iterator to walk puzzles in the active split.

    Parameters
    - root (str or Path): path to the dataset root folder. In manaeged mode, this is where data will be downloaded/extracted.
    - version (str): dataset version. Supported versions are: 'v2', 'v2.0.1', 'v2.0.2', 'v2.5b'.
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
                 version=None,
                 type_=None,
                 managed_mode=True,
                 split=None,
                 supervised_mode=False,
                 from_scratch=False,
                 skip_verify=False) -> None:
        
        
        self.root = Path(root)
        
        self._split = split
        self.supervised_mode = supervised_mode

        # iterator state
        self._iter_idx = 0
        
        
        if version is None:
            if managed_mode:
                # if we manage the data, we set the default version type
                version = DEFAULT_VERSION
            else:
                raise RuntimeError("When managed_mode is False, version must be specified.")
        
        if type_ is None:
            if managed_mode:
                # if we manage the data, we set the default version type
                type_ = DEFAULT_TYPE
            else:
                raise RuntimeError("When managed_mode is False, type_ must be specified.")

        self.version_type = VersionType(version, type_)

        if not self.version_type.supported(SUPPORTED_VERSIONS_TYPES):
            raise RuntimeError(f"Unsupported dataset version_type {self.version_type}. Supported versions are:\n {SUPPORTED_VERSIONS_TYPES}")
        
        if managed_mode:
            mvt = self.version_type.major_version_type()
            remote = REMOTES.get(mvt, None)

            if remote is None:
                raise RuntimeError(f"Remote missing for major version_type {mvt}.")

            self.datamanager = DataManager(
                root=self.root,
                version_type=self.version_type,
                remote=remote,
                from_scratch=from_scratch,
                skip_verify=skip_verify,
                patch_map=PATCH_MAP,
            )

        ################### Load dataset ###################

        #print(f'Loading RePAIRDataset {self.version_type}')

        self.data_path = self.datamanager.data_path if managed_mode else self.root
        
        err_msg = "Check the specified root folder is correct. If the error persist, try to recreate the dataset running with from_scratch=True or by deleting the root folder."
        if not self.data_path.exists():
            if managed_mode:
                raise RuntimeError(f"Cannot find data folder. {err_msg}")
            else:
                raise RuntimeError("Dataset path does not exist. Check the specified root folder is correct.")

        self.puzzle_folders_list = [p for p in self.data_path.iterdir() if p.is_dir() and p.name.startswith("puzzle_")]

        self._make_split()

        if len(self.puzzle_folders_list) == 0:
            if managed_mode:
                raise RuntimeError(f"No data found after extraction. The dataset may be corrupted. {err_msg}")
            else:
                raise RuntimeError("No data found in the specified root folder.")
    
    def _make_split(self) -> None:

        split = None

        if self._split is not None:
            if self._split == 'train':
                split = train_split
            elif self._split == 'test':
                split = test_split
            else:
                raise RuntimeError(f"Unsupported split name: {self._split}. Supported splits are: 'train', 'test'")
        
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
    
    def _get_metadata(self, key : Union[int, str]) -> dict:
        if isinstance(key, int):
            puzzle_folder = self.puzzle_folders_list[key]
        elif isinstance(key, str):
            puzzle_folder = self.puzzle_folders_list[self.puzzle_folders_map[key]]
        else:
            raise TypeError(f"Invalid key type: {type(key)}")

        json_path = puzzle_folder / "data.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        data['path'] = str(puzzle_folder)

        return data

    def __getitem__(self, key : Union[int, str]) -> Union[dict, tuple]:

        # this should not happen, but just in case
        if self.version_type.type_ != '2D_SOLVED' :
            raise NotImplementedError(f"Dataset type {self.version_type.type_} not implemented yet.")

        if self.version_type.version.major() == 1:
            raise NotImplementedError("v1 datasets are not supported yet.")

        data = self._get_metadata(key)

        puzzle_folder = Path(data['path'])

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

        if not self.supervised_mode:
            return data
        
        ######## SUPERVISED MODE ########
        
        # in this case self.supervised_mode is True
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
