from pathlib import Path
from typing import Union

from .splits.splits import train_split, test_split

from datman import DataManager
from .variant_version import VariantVersion, Version

from .getters.solved2d_getter import getmetadata_2dsolved, getitem_2dsolved
from .getters.solved3d_getter import getitem_3dsolved

from .info import (
    VARIANTS,
    REMOTES,
    assert_supervised_mode,
)


class RePAIRDataset:

    def __init__(self,
                 root,
                 version=None,
                 variant=None,
                 apply_random_rotations=False,
                 managed_mode=True,
                 split=None,
                 supervised_mode=False,
                 from_scratch=False,
                 skip_verify=False) -> None:
        
        
        self.root = Path(root)
        
        self._split = split
        self.supervised_mode = supervised_mode
        self.apply_random_rotations = apply_random_rotations

        # iterator state
        self._iter_idx = 0

        if variant is None or variant == '':
            raise RuntimeError("Dataset type must be specified.")
        
        if variant not in VARIANTS:
            raise RuntimeError(f"Unsupported dataset type: {variant}. Supported types are: {list(VARIANTS.keys())}")
 
        if not version:
            if managed_mode:
                ver = VARIANTS[variant]['default_version']
            else:
                raise RuntimeError("When managed_mode is False, version must be specified.")
        else:
            ver = Version.parse(version)

        supported_versions = VARIANTS[variant]['versions']
        filtered_versions = [v for v in supported_versions if ver.matches(v)]
        if len(filtered_versions) == 0:
            raise RuntimeError(f"Unsupported version {ver} for dataset type {variant}. Supported versions are: {[str(v) for v in list(supported_versions.keys())]}")

        matched_version = max(filtered_versions)

        self.variant_version = VariantVersion(matched_version, variant)

        if self.supervised_mode:
            assert_supervised_mode(variant, matched_version)

        print(f"RePAIRDataset {self.variant_version}")

        version_dict = supported_versions[matched_version]

        #################### Args checks ###################

        if apply_random_rotations:
            if variant != '2D_SOLVED':
                raise RuntimeError("Random rotations can only be applied to '2D_SOLVED' dataset type.")
        
            if not supervised_mode:
                raise RuntimeError("Random rotations can only be applied in supervised mode.")

        #################### DataManager setup ###################

        self.datamanager = None

        if managed_mode:
            
            base = version_dict.get('base', self.variant_version.version)
            remote = REMOTES.get(f"{self.variant_version.variant}_v{base}", None)
            if remote is None:
                raise RuntimeError(f"Remote missing for base dataset variant {self.variant_version.variant} and version {base}.")

            self.datamanager = DataManager(
                root=self.root,
                dataset_id=str(self.variant_version),
                remote=remote,
                extract_subpath= f"{self.variant_version.variant}/v{self.variant_version.version}",
                from_scratch=from_scratch,
                skip_verify=skip_verify,
                patches=version_dict.get('patches',[])
            )

        ################### Load dataset ###################

        self.data_path = self.datamanager.data_path if self.datamanager is not None else self.root
        
        err_msg = "Check the specified root folder is correct. If the error persist, try to recreate the dataset running with from_scratch=True or delete the STATUS file inside the folder."
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
        puzzle_folder = self._get_puzzle_folder(key)
        if self.variant_version.variant != '2D_SOLVED':
            raise NotImplementedError(f"Metadata getter not implemented for dataset type {self.variant_version.variant}.")
        return getmetadata_2dsolved(puzzle_folder)

    def _get_puzzle_folder(self, key) -> Union[str, Path]:
        if isinstance(key, int):
            puzzle_folder = self.puzzle_folders_list[key]
        elif isinstance(key, str):
            puzzle_folder = self.puzzle_folders_list[self.puzzle_folders_map[key]]
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
        return puzzle_folder

    def __getitem__(self, key : Union[int, str]) -> Union[dict, tuple]:
        puzzle_folder = self._get_puzzle_folder(key)
        # this should not happen, but just in case
        if self.variant_version.variant == '2D_SOLVED' :
            return getitem_2dsolved(puzzle_folder, self.supervised_mode, self.apply_random_rotations)
        elif self.variant_version.variant == '3D_SOLVED':
            return getitem_3dsolved(puzzle_folder, self.supervised_mode)
        else:
            raise NotImplementedError(f"Dataset type {self.variant_version.variant} not implemented yet.")



    
   