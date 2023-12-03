from Magisk import Magisk_patch, os, sys
if __name__ == '__main__':
    if sys.argv.__len__() < 2:
        print("参数不足")
        print("默认修补:./patch [boot.img]")
        print("自定义修补:./patch [boot.img] [Magisk.apk]")
        print("自定义修补指定架构:./patch [boot.img] [Magisk.apk] [ARCH]")
    elif sys.argv.__len__() == 2:
        Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk')).auto_patch()
    elif sys.argv.__len__() == 3:
        Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk'), MAGISAPK=sys.argv[2]).auto_patch()
    elif sys.argv.__len__() == 4:
        Magisk_patch(os.path.abspath(sys.argv[1]), os.path.join(os.getcwd(), 'bin', 'Magisk'), MAGISAPK=sys.argv[2], PATCH_ARCH=sys.argv[3]).auto_patch()
