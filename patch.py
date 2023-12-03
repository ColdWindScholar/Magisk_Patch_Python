from Magisk import Magisk_patch, os, sys
from log import LOGE
if __name__ == '__main__':
    if sys.argv.__len__() < 2:
        LOGE("参数不足")
        LOGE("默认修补:./patch [boot.img]")
        LOGE("自定义修补:./patch [boot.img] [Magisk.apk]")
        LOGE("自定义修补指定架构:./patch [boot.img] [Magisk.apk] [ARCH]")
    elif sys.argv.__len__() == 2:
        with Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk')) as patch:
            patch.auto_patch()
    elif sys.argv.__len__() == 3:
        with Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk'), MAGISAPK=sys.argv[2]) as patch:
            patch.auto_patch()
    elif sys.argv.__len__() == 4:
        with Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk'), MAGISAPK=sys.argv[2], PATCH_ARCH=sys.argv[3]) as patch:
            patch.auto_patch()
