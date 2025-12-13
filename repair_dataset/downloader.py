import requests
import hashlib
from tqdm import tqdm
from pathlib import Path

class DownloaderVerifier:
    def __init__(self,
                 folder,
                 data_url,
                 filename,
                 file_sha256_digest=None,
                 skip_checksum=False):

        self.folder = Path(folder)
        self.data_url = data_url
        self.file_path = self.folder / filename
        self.digest = file_sha256_digest
        self.extract_path = self.folder

        self.skip_checksum = skip_checksum

    def download(self):
        self.folder.mkdir(parents=True, exist_ok=True)

        # Download zip if not present or checksum fails
        verified = self.verify(self.file_path) if self.file_path.exists() else False
        if not self.file_path.exists() or not verified:
            if self.file_path.exists() and not verified:
                print("Existing file checksum does not match, re-downloading...")

            download(
                url=self.data_url,
                file_path=self.file_path,
                verify_checksum_func=self.verify
            )
    
    def verify(self, file_path):
        return verify_checksum(file_path, self.digest, self.skip_checksum)
    
################# Helper functions #################

def verify_checksum(file_path, expected_digest, skip):
    if skip:
        return True

    return checksum(file_path) == expected_digest

def checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def download(url, file_path, verify_checksum_func):
    tmp_path = file_path.with_suffix(".zip.part")  # Temporary download file

    print(f"Downloading {url} ...")
    response = requests.get(url, stream=True)
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
    if verify_checksum_func and not verify_checksum_func(tmp_path):
        tmp_path.unlink()  # remove incomplete/invalid download
        raise RuntimeError("Downloaded file checksum does not match! Try downloading again. If the problem persists, set skip_checksum=True at your own risk.")

    tmp_path.rename(file_path)  # rename only after successful download
