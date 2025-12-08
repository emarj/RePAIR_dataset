import zipfile
import requests
import hashlib
from tqdm import tqdm
from pathlib import Path
from torch.utils.data import Dataset
from abc import ABC, abstractmethod

class DownloadableDatasetBase(ABC,Dataset):
    def __init__(self,
                 root,
                 data_url,
                 zip_filename='data.zip',
                 data_name="data",
                 data_sha256_digest=None,
                 download=True,
                 skip_checksum=False):

        self.root = Path(root)
        self.data_url = data_url
        self.zip_path = self.root / zip_filename
        self.digest = data_sha256_digest
        self.extract_path = self.root
        self.data_path = self.extract_path / data_name

        self.skip_checksum = skip_checksum

        if download:
            self._download_and_extract()


    def _verify_checksum(self, filepath):
        if self.skip_checksum:
            return True
        
        if self.digest is None:
            raise ValueError("No SHA256 digest provided for checksum verification.")
        
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest() == self.digest

    def _download_and_extract(self):
        self.root.mkdir(parents=True, exist_ok=True)

        # Download zip if not present or checksum fails
        verified = self._verify_checksum(self.zip_path) if self.zip_path.exists() else False
        if not self.zip_path.exists() or not verified:
            if self.zip_path.exists() and not verified:
                print("Existing file checksum does not match, re-downloading...")

            tmp_path = self.zip_path.with_suffix(".zip.part")  # Temporary download file

            print(f"Downloading {self.data_url} ...")
            response = requests.get(self.data_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 1024

            with open(tmp_path, "wb") as f, tqdm(
                total=total_size, unit='B', unit_scale=True, desc="Downloading"
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            # Verify checksum before renaming
            if not self._verify_checksum(tmp_path):
                tmp_path.unlink()  # remove incomplete/invalid download
                raise RuntimeError("Downloaded file checksum does not match! Try downloading again. If the problem persists, set skip_checksum=True at your own risk.")

            tmp_path.rename(self.zip_path)  # rename only after successful download
            print("Download complete and verified.")

        # Extract if not already extracted
        if not self.data_path.exists():
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                for file in tqdm(file_list, desc="Extracting"):
                    zip_ref.extract(file, self.extract_path)


    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, idx):
        pass