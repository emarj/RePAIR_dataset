# RePAIR_dataset

## Install
You can install the package from the repository using pip (or your preferred package manager). Example:

- From a local checkout:
    pip install .
- From a remote repo (replace URL with the repository URL):
    pip install git+https://github.com/youruser/yourrepo.git

We recommend using an isolated environment (venv/virtualenv).

## Quick usage

Example file (managed mode — the DataManager handles extraction/patching):
```python
from repair_dataset import RePAIRDataset

dataset = RePAIRDataset('.dataset/RePAIR',
                                                version='v2',
                                                type_='2D_SOLVED',
                                                split='test',
                                                from_scratch=False,
                                                supervised_mode=True)  # set True to return images

print(f"Number of samples: {len(dataset)}")
x, data = dataset[0]  # if supervised_mode=True
# if supervised_mode=False, dataset[0] returns the parsed metadata dict
```

Manual/unmanaged usage (you already have the dataset on disk):
```python
from repair_dataset import RePAIRDataset

dataset = RePAIRDataset('/path/to/RePAIR_root',
                                                version='v2',
                                                type_='2D_SOLVED',
                                                managed_mode=False,
                                                supervised_mode=False)  # metadata only
data = dataset['puzzle_0001']  # access by folder name
```

## Modes

- supervised_mode=True
    - __getitem__ returns (x, data)
    - x = {'name': <puzzle_name>, 'fragments': [{'idx', 'name', 'image': PIL.Image}, ...]}
    - data = original JSON metadata (with 'path' and 'name' injected for v2)

- supervised_mode=False (default)
    - __getitem__ returns the parsed metadata dict only (no in-memory images)

Other notes:
- You can iterate over the dataset (for puzzle in dataset: ...).
- Use split='train' or split='test' to filter puzzles by provided splits.
- When managed_mode=False you must provide version and type_ explicitly.
- For v2 variants, fragment filenames in JSON may be .obj on disk images are loaded as .png (handled automatically when supervised_mode=True).