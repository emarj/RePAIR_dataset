import enum
from pathlib import Path
import shutil
import zipfile

from tqdm import tqdm

from .downloader import DownloaderVerifier


DATA_URL = "https://zenodo.org/records/15800029/files/2D_SOLVED.zip?download=1"
DATA_SHA256 = "5361bcfb8be82424f39302d0530acf1a97456672527e2d720f1ad55b28ba87a7"
DATA_FILENAME = "2D_SOLVED.zip"
DATA_NAME = "SOLVED"

class Status(enum.Enum):
    NONE = 'NONE'
    OK = 'OK'

class DataManager(DownloaderVerifier):
    def __init__(self,
                 root,
                 version=None,
                 from_scratch=False,
                 patch_map=None,
                 skip_verify=False):

        self.root = Path(root)

        self.dv = DownloaderVerifier(
            folder=self.root,
            data_url=DATA_URL,
            filename=DATA_FILENAME,
            file_sha256_digest=DATA_SHA256,
            skip_checksum=skip_verify
        )

        self.version = version
        if version is None:
            self.version = "unknown"
            self.data_path = self.root / DATA_NAME
        else:
            self.data_path = self.root / self.version / DATA_NAME

        self.status_file_path = self.root / 'STATUS'

        self.patch_map = patch_map if patch_map is not None else {}

        ##### Setup #####

        if from_scratch:
            self.set_status(Status.NONE)

        self._download_and_extract()

    def get_status(self):
        if not self.status_file_path.exists():
            return Status.NONE
        
        statuses = load_kv(self.status_file_path)
        status_str = statuses.get(self.version, 'NONE')
        try:
            return Status(status_str)
        except ValueError:
            print(f"Unknown status '{status_str}' in status file. Treating as NONE.")
            return Status.NONE
        
    
    def set_status(self, status: Status):
        statuses = load_kv(self.status_file_path) if self.status_file_path.exists() else {}
        statuses[self.version] = status.value
        save_kv(self.status_file_path, statuses)
        

    def _download_and_extract(self):
        
        # downloader manages its own state
        self.dv.download()

        status = self.get_status()
        if status == Status.OK:
            return
        
        self._extract()
        self._apply_patches()

        self.set_status(Status.OK)

        print(f"Dataset version {self.version} is ready")
        

    def _extract(self):
        self.extract_path = self.root / self.version

        if self.extract_path.exists():
            # if we decided to extract, it means we want a fresh copy
            shutil.rmtree(self.extract_path)

        self.extract_path.mkdir(parents=True, exist_ok=False)

        with zipfile.ZipFile(self.dv.file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file in tqdm(file_list, desc="Extracting", disable=False):
                zip_ref.extract(file, self.extract_path)


    def _apply_patches(self) -> None:
        # patches_map = {
        #     'v2.0.1': [patch_v2_0_1],
        #     'v2.0.2': [patch_v2_0_1, patch_v2_0_2],
        #     'v3-beta': [convert_to_v3],
        # }

        if self.version not in self.patch_map:
            return
        patches = self.patch_map[self.version]
        print(f"Applying {len(patches)} patches...")

        for patch_func in patches:
            patch_func(str(self.data_path))

##### Utility functions for key-value file handling

def load_kv(file_path):
    data = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                key, value = line.split(":", 1)
                data[key] = value

    return data

def save_kv(file_path, data):
    with open(file_path, "w") as f:
        for key, value in data.items():
            f.write(f"{key}:{value}\n")