# RePAIR_dataset

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

## Select a patched version

Available versions:
- v2: vanilla one
- v2.0.1: vanilla one with fixed some mistakes
- v2.0.2: 
- v2.5b: beta version with corrected GT and metadata v3

```python
from repair_dataset import RePAIRDataset

dataset = RePAIRDataset('.dataset/RePAIR',
                        version='v2.5b',
                        supervised_mode=True)

print(f"Number of samples: {len(dataset)}")

x, data = dataset[0]  # if supervised_mode=True
# if supervised_mode=False, dataset[0] returns the parsed metadata dict
```
