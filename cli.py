import argparse

from repair_dataset.dataset import RePAIRDataset


def parse_args():
    parser = argparse.ArgumentParser(description="Instantiate RePAIRDataset with provided arguments")

    parser.add_argument('root', help='Path to dataset root folder')

    parser.add_argument('--version', help="Dataset version (e.g. 'v2.0.1')", default=None)
    parser.add_argument('--type', dest='type_', help="Dataset type (e.g. '2D_SOLVED')", default=None)

    parser.add_argument('--split', choices=['train', 'test'], help="Optional split to load", default=None)

    parser.add_argument('--supervised', dest='supervised_mode', action='store_true', help='Return images with data')
    parser.add_argument('--unmanaged', dest='managed_mode', action='store_false', help='Do not use DataManager')

    parser.add_argument('--from-scratch', dest='from_scratch', action='store_true', help='Force fresh extraction')
    parser.add_argument('--skip-verify', dest='skip_verify', action='store_true', help='Skip integrity checks')

    return parser.parse_args()


def main():
    args = parse_args()

    
    ds = RePAIRDataset(
        root=args.root,
        version=args.version,
        type_=args.type_,
        split=args.split,
        managed_mode=args.managed_mode,
        supervised_mode=args.supervised_mode,
        from_scratch=args.from_scratch,
        skip_verify=args.skip_verify,
    )

    print(f"Number of puzzles: {len(ds)}")


if __name__ == '__main__':
    main()
