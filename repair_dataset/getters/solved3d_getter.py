def getitem_3dsolved(puzzle_folder, supervised_mode) -> dict:

        if supervised_mode:
            raise NotImplementedError("3D_SOLVED dataset not available in supervised mode.")

        frags = {}
        for file in puzzle_folder.iterdir():
            if file.suffix.lower() in ['.mtl', '.obj', '.png']:
                frag_name = file.stem
                if frag_name not in frags:
                    frags[frag_name] = {
                        'name': frag_name,
                    }
                frags[frag_name][file.suffix.lower()[1:]] = str(file)

        
        for frag in frags.values():
            if 'obj' not in frag or 'mtl' not in frag or 'png' not in frag:
                raise RuntimeError(f"Fragment {frag['name']} is missing one of the required files (.obj, .mtl, .png)")
            

        data = {
            'path': str(puzzle_folder),
            'name': puzzle_folder.name,
            'fragments': list(frags.values()),
        }

        return data

