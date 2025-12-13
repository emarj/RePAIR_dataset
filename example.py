from repair_dataset import RePAIRDataset

def main():

    dataset = RePAIRDataset('.dataset/RePAIR_v2/v2.0.2/SOLVED',
                               version='v2.0.2',
                               split='test',
                               from_scratch=False,
                               managed_mode=False)

    print(f"Number of samples in dataset: {len(dataset)}")
    
    sample = dataset[0]
    print(sample)
    

if __name__ == "__main__":
    main()
