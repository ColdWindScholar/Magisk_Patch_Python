import sys
import os
from Magisk import Magisk_patch
if __name__ == '__main__':
    if sys.argv.__len__() < 2:
        print("参数不足")
        print("用法:./patch [boot.img]")
    else:
        Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk')).auto_patch()
