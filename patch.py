import sys
import os
from Magisk import Magisk_patch
if __name__ == '__main__':
    Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk')).auto_patch()
