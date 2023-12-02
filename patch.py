import sys

import os
from Magisk import Magisk_patch

local = os.getcwd()


def patch(boot_img):
    Magisk_patch(os.path.abspath(boot_img), os.path.join(local, 'bin', 'Magisk')).auto_patch()


if __name__ == '__main__':
    patch(sys.argv[1])
