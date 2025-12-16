from .patches.patch_2ds_v3b import patch_2ds_v3b
from .patches.patch_2ds_v2_0_1 import patch_2ds_v2_0_1
from .patches.patch_2ds_v2_0_2 import patch_2ds_v2_0_2

VERSIONS_TYPES = {
    '2D_SOLVED': {
        'default_version': 'v2.0.2',
        'versions': {'v2': {},
                  'v2.0.1': {
                        'base': 'v2',
                        'patches': ['patch_2ds_v2_0_1'],
                  },
                  'v2.0.2': {
                        'base': 'v2',
                        'patches': ['patch_2ds_v2_0_1', 'patch_2ds_v2_0_2'],
                  },
                  'v3b': {
                        'base': 'v2',
                        'patches': ['patch_2ds_v3b'],
                  },
                  },
    },
    '3D_SOLVED': {
        'default_version': 'v2',
        'versions': {'v2': {}}},
    }


REMOTES = {
    "2D_SOLVED_v2": {
        "url": "https://zenodo.org/records/15800029/files/2D_SOLVED.zip?download=1",
        "checksum": "md5:8fd40f910b10ea1e02e4db4b57df8eb9",
        "filename": "2D_SOLVED_v2.zip",
        "folder_name": "SOLVED",
    },
    "3D_SOLVED_v2": {
        "url": "https://zenodo.org/records/15800029/files/3D_SOLVED.zip?download=1",
        "checksum": "md5:8bfa13e1d5de5528cda22c72a47103e8",
        "filename": "3D_SOLVED_v2.zip",
        "folder_name": "SOLVED",
    }
}
