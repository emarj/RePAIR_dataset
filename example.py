from repair_dataset import RePAIRDataset

def main():

    dataset = RePAIRDataset('.dataset/RePAIR',
                               version='v2',
                               type_='2D_SOLVED',
                               supervised_mode=True)

    print(f"Number of samples in dataset: {len(dataset)}")
    
    sample = dataset[0]
    print(sample)
    

if __name__ == "__main__":
    main()
