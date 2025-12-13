from repair_dataset import RePAIRDataset
from repair_dataset.splits.splits import train_split, test_split

TEST_DS_PATH = ".dataset/RePAIR_v2"

def test_splits() -> None:
    dataset = RePAIRDataset(TEST_DS_PATH)
    assert len(set(test_split)) == len(test_split)
    assert len(set(train_split)) == len(train_split)

    assert len(set(train_split).intersection(set(test_split))) == 0

    assert len(test_split) + len(train_split) == len(dataset)

def test_dataset() -> None:
  
    dataset_train = RePAIRDataset(TEST_DS_PATH, split="train")
    dataset_test = RePAIRDataset(TEST_DS_PATH, split="test")

    assert len(dataset_train) == len(train_split)
    assert len(dataset_test) == len(test_split)