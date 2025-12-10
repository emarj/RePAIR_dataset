from repair_dataset import RePAIRDataset

dataset = RePAIRDataset("../datasets/RePAIR_dataset/v2", split="train")

print(f"Number of samples: {len(dataset)}")
sample = dataset[8]
print(sample)  # This is the dict from data.json
