from repair_dataset.patches import patch_2ds_v3_b2
from .patches.patch_2ds_v3_b1 import patch_2ds_v3_b1
from .patches.patch_2ds_v2_0_1 import patch_2ds_v2_0_1
from .patches.patch_2ds_v2_0_2 import patch_2ds_v2_0_2

from .variant_version import Version

from datman.remote import Remote

VARIANTS = {
    '2D_SOLVED': {
        'default_version': Version.parse('3'),
        'versions': {
                  Version.parse('2'): {},
                  Version.parse('2.0.1'): {
                        'base': Version.parse('2'),
                        'patches': [patch_2ds_v2_0_1],
                  },
                  Version.parse('2.0.2'): {
                        'base': Version.parse('2'),
                        'patches': [patch_2ds_v2_0_1, patch_2ds_v2_0_2],
                  },
                  Version.parse('3-beta.1'): {
                        'base': Version.parse('2'),
                        'patches': [patch_2ds_v3_b1],
                  },
                  Version.parse('3-beta.2'): {
                        'base': Version.parse('2'),
                        'patches': [patch_2ds_v3_b1,patch_2ds_v3_b2],
                  },
                  },
    },
    '3D_SOLVED': {
        'default_version': Version.parse('2'),
        'versions': {Version.parse('2'): {}}},
    }



REMOTES = {
    "2D_SOLVED_v2": Remote(
        url="https://zenodo.org/records/15800029/files/2D_SOLVED.zip?download=1",
        checksum="md5:8fd40f910b10ea1e02e4db4b57df8eb9",
        filename="2D_SOLVED_v2.zip",
        root_folder="SOLVED",
    ),
    "3D_SOLVED_v2": Remote(
        url="https://zenodo.org/records/15800029/files/3D_SOLVED.zip?download=1",
        checksum="md5:8bfa13e1d5de5528cda22c72a47103e8",
        filename="3D_SOLVED_v2.zip",
        root_folder="SOLVED",
    )
}
