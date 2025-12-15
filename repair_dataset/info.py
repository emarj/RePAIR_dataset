from .patches.patch_2ds_v2_5_0b import patch_2ds_v2_5_0b
from .patches.patch_2ds_v2_0_1 import patch_2ds_v2_0_1
from .patches.patch_2ds_v2_0_2 import patch_2ds_v2_0_2


DEFAULT_VERSION = 'v2.0.1'
DEFAULT_TYPE = '2D_SOLVED'

SUPPORTED_VERSIONS_TYPES = {
    '2D_SOLVED': ['v1', 'v2', 'v2.0.1', 'v2.0.2', 'v2.5b'],
    '3D_SOLVED': ['v2'],
    }

PATCH_MAP = {
            '2D_SOLVED_v2.0.1': [patch_2ds_v2_0_1],
            '2D_SOLVED_v2.0.2': [patch_2ds_v2_0_1, patch_2ds_v2_0_2],
            '2D_SOLVED_v2.5b': [patch_2ds_v2_5_0b],
            }

REMOTES = {
    # "2D_Fragments_v1": {
    #     "url": "https://zenodo.org/records/13993089/files/2D_Fragments.zip?download=1",
    #     "hash": "???",
    #     "filename": "2D_Fragments_v1.zip",
    #     "folder_name": "2D_Fragments",
    # },
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
