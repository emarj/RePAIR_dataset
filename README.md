# RePAIR_dataset

Python implementation of [RePAIR Dataset](https://zenodo.org/records/15800029).

## Install
You can install the package from the repository using `pip` or your preferred package manager (usgin `uv` is suggested). 

### User mode

To install and import the package in your project run
```bash
# standard pip command
pip install git+https://github.com/emarj/RePAIR_dataset.git
# uv in project mode
uv add git+https://github.com/emarj/RePAIR_dataset.git
# uv in venv only mode
uv pip install git+https://github.com/emarj/RePAIR_dataset.git 
```

### Dev mode
If you want to play with it, checkout the repo
```bash
git clone https://github.com/emarj/RePAIR_dataset.git
```

```bash
uv sync
```
this will automatically create a `venv` for you. Otherwise
```bash
# create your venv
pip install .
```

## Usage (Managed Mode)

Use it as
```python
from repair_dataset import RePAIRDataset

dataset = RePAIRDataset('.dataset/RePAIR', supervised_mode=True)

print(f"Number of samples: {len(dataset)}")

x, data = dataset[0]  # if supervised_mode=True
# if supervised_mode=False, dataset[0] returns the parsed metadata dict
```
downloads will be managed automatically.

### Select a patched version

Available versions:
- v2: vanilla v2, as downloaded from Zenodo
- v2.0.1: fixing some major GT errors on 3 puzzles
- v2.0.2: fixing filenames in metadata '.obj' -> '.png'
- v3b: beta version with corrected GT and new metadata version

```python
from repair_dataset import RePAIRDataset

dataset = RePAIRDataset('.dataset/RePAIR',
                        version='v3b',
                        supervised_mode=True)

print(f"Number of samples: {len(dataset)}")

x, data = dataset[0]  # if supervised_mode=True
# if supervised_mode=False, dataset[0] returns the parsed metadata dict
```

## Usage (Unmanaged mode)
To be written

## Supported datasets

| Type   | Supported | Supervised | Versions |
|----------|----------|----------|----------|
| 2D_SOLVED   | ✅   |  ✅  | v2, v2.0.1, v2.0.2, v3b   |
| 2D_OPEN_DISCOVERY    | ❌   |  -  | -  |
| 3D_SOLVED    | ✅   | ❌   | v2   |
| 3D_OPEN_DISCOVERY    | ❌   | -   | -   |

### Applying patches
To be written

## Evaluate
To be written
