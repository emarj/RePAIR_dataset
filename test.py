from repair_dataset import RePAIRDataset
from repair_dataset.split import train_split, test_split


def test_splits() -> None:
    dataset = RePAIRDataset("./dataset")
    assert len(set(test_split)) == len(test_split)
    assert len(set(train_split)) == len(train_split)

    assert len(set(train_split).intersection(set(test_split))) == 0

    assert len(test_split) + len(train_split) == len(dataset)

def test_dataset() -> None:
  
    dataset_train = RePAIRDataset("./dataset", split="train")
    dataset_test = RePAIRDataset("./dataset", split="test")

    assert len(dataset_train) == len(train_split)
    assert len(dataset_test) == len(test_split)

    train_names = set(p.name for p in dataset_train.sample_folders)
    test_names = set(p.name for p in dataset_test.sample_folders)

    assert train_names == set(train_split)
    assert test_names == set(test_split)