import os
from .downloadable import DownloadableDatasetBase
from .utils import load_data_json


DATA_URL = "https://zenodo.org/records/15800029/files/2D_SOLVED.zip?download=1"
DATA_SHA256 = "5361bcfb8be82424f39302d0530acf1a97456672527e2d720f1ad55b28ba87a7"
DATA_FILENAME = "2D_SOLVED.zip"


class RePAIRDataset(DownloadableDatasetBase):
    def __init__(self, root, split=None, download=True, skip_checksum=False):
        
        super().__init__(root,
                         data_url=DATA_URL,
                         zip_filename=DATA_FILENAME,
                         data_name="SOLVED",
                         data_sha256_digest=DATA_SHA256,
                         download=download,
                         skip_checksum=skip_checksum)

        
        self.sample_folders = [p for p in self.data_path.iterdir() if p.is_dir() and p.name.startswith("puzzle_")]
        # sort puzzles, better for reproducibility
        self.sample_folders = sorted(self.sample_folders, key=lambda p: str(p))
        # split using split
        self._split(split)


        if len(self) == 0:
            raise RuntimeError("No data found after extraction. The dataset may be corrupted.")

    def _split(self, split):
        if split:
            if split == "train":
                from repair_dataset.split import train_split
                selected = set(train_split)
            elif split == "test":
                from repair_dataset.split import test_split
                selected = set(test_split)
            else:
                raise ValueError(f"Unknown split: {split}")

            self.sample_folders = [p for p in self.sample_folders if p.name in selected]
   
    def __len__(self):
        return len(self.sample_folders)

    def __getitem__(self, idx):
        puzzle_folder = self.sample_folders[idx]
        json_path = puzzle_folder / "data.json"

        data = load_data_json(str(json_path))

        for i,frag in enumerate(data['fragments']):
            data['fragments'][i]['image_path'] = os.path.join(str(puzzle_folder), frag['filename'].replace('.obj', '.png'))

        out = {'name': puzzle_folder.name,
             'fragments': [{
                'idx': frag['idx'],
                'image_path': frag['image_path'],
            } for frag in data['fragments']],
            'data': data,
            }

        return out
