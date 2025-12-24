import random

from repair_dataset import RePAIRDataset
from repair_dataset.reconstruct import reassemble_2d
from repair_dataset.utils import create_image_grid

def main():

    dataset = RePAIRDataset('.dataset/RePAIR',
                               version='3',
                               variant='2D_SOLVED',
                               supervised_mode=True,
                               apply_random_rotations=True,
                               )

    print(f"Number of samples in dataset: {len(dataset)}")
    
    idx = random.randint(0, len(dataset) - 1)
    idx = 0
    print(f"Fetching sample at index {idx}...")

   
    
    sample = dataset[idx]
    print(sample)

    #create_image_grid(sample[0]['fragments']).show()

    #breakpoint()

    # inject positions to obtain "solved" fragments
    solved_fragments = sample[0]['fragments']
    for i, frag in enumerate(solved_fragments):
        solved_fragments[i]['position_2d'] = sample[1]['fragments'][i]['position_2d']
    


    reassembled_image = reassemble_2d(solved_fragments, solution_size=sample[1]['solution_size'])
    reassembled_image.show()

if __name__ == "__main__":
    main()
