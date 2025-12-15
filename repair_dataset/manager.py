import enum
from pathlib import Path
import shutil
import zipfile

from tqdm import tqdm

from .downloader import DownloaderVerifier
from .version_type import VersionType

class Status(enum.Enum):
    NONE = "NONE"
    OK = "OK"


class DataManager(DownloaderVerifier):
    def __init__(
        self, root, version_type, remote, from_scratch=False, patch_map=None, skip_verify=False
    ):
        if isinstance(version_type, VersionType):
            self.version_type = version_type
        else:
            self.version_type = VersionType.from_str(version_type)

        self.root = Path(root)

        if not self.root.exists():
            self.root.mkdir(parents=True, exist_ok=False)

        write_readme(self.root)
        
        self.extract_path = self.root / self.version_type.type_ / str(self.version_type.version)
        self.data_path = self.extract_path / remote["folder_name"]
        self.status_file_path = self.root / "STATUS"

        self.dv = DownloaderVerifier(
            folder=self.root,
            data_url=remote["url"],
            filename=remote["filename"],
            checksum=remote["checksum"],
            skip_verify=skip_verify,
        )

        self.patch_map = patch_map if patch_map is not None else {}

        ##### Setup #####

        if from_scratch:
            self.set_status(Status.NONE)

        self._download_and_extract()

    

    def _download_and_extract(self):
        # downloader manages its own state
        self.dv.download()

        status = self.get_status()
        if status == Status.OK:
            return

        self._extract()
        self._apply_patches()

        self.set_status(Status.OK)

        print(f"Dataset version {self.version_type} is ready")

    def _extract(self):

        if not self.dv.file_path.exists():
            raise RuntimeError(f"Cannot extract, file {self.dv.file_path} does not exist.")

        if self.extract_path.exists():
            # if we decided to extract, it means we want a fresh copy
            shutil.rmtree(self.extract_path)

        self.extract_path.mkdir(parents=True, exist_ok=False)

        with zipfile.ZipFile(self.dv.file_path, "r") as zip_ref:
            file_list = zip_ref.namelist()
            for file in tqdm(file_list, desc="Extracting", disable=False):
                zip_ref.extract(file, self.extract_path)

    def _apply_patches(self) -> None:
        # patches_map = {
        #     'v2.0.1_typeA': [patch_2ds_v2_0_1],
        #     'v2.0.2_typeA': [patch_2ds_v2_0_1, patch_2ds_v2_0_2],
        #     'v3.0.1_typeB': [patch_2ds_v3_0_1],
        # }

        patches = self.patch_map.get(str(self.version_type), [])

        if len(patches) == 0:
            print("No patches to apply.")
            return
        
        print(f"Applying {len(patches)} patches...")

        for patch_func in patches:
            patch_func(str(self.data_path))

    ######## Status management ########

    def get_status(self):
        if not self.status_file_path.exists():
            return Status.NONE

        statuses = load_kv(self.status_file_path)
        status_str = statuses.get(str(self.version_type), "NONE")
        try:
            return Status(status_str)
        except ValueError:
            print(f"Unknown status '{status_str}' in status file. Treating as NONE.")
            return Status.NONE

    def set_status(self, status: Status):
        statuses = (
            load_kv(self.status_file_path) if self.status_file_path.exists() else {}
        )
        statuses[str(self.version_type)] = status.value
        save_kv(self.status_file_path, statuses)

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

##### README to insert into root folder #####

README = """DO NOT TOUCH the contents of this folder unless you know what you are doing. In particular, do not delete the zip archives.
This folder is managed by a dataset data manager, which handles downloading, verifying, extracting files.
If something do not work as expected, try to use `from_scratch=True` option or delete the `STATUS` file to force re-download and re-extraction.

This behaviour can be disabled by using unmanaged mode in the dataset, but then you are responsible for having the correct data in place.

If you want to free space, you cannot delete the zip files, they will be re-downloaded automatically if missing.
You can delete the extracted data folders for versions you do not need anymore, the major version folder (v2) is always necessary."""

def write_readme(folder_path):
    with open(folder_path / "README", "w") as f:
        f.write(README)