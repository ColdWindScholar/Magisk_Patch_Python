import hashlib
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from log import LOGE, LOGW, yecho, LOGS

local = os.getcwd()


class Magisk_patch:

    def __init__(self, boot_img, Magisk_dir, IS64BIT=True, KEEPVERITY=False, KEEPFORCEENCRYPT=False,
                 RECOVERYMODE=False, MAGISAPK=None, PATCH_ARCH=None):
        self.SKIPBACKUP = ''
        self.SKIPSTUB = ''
        self.SKIP64 = ''
        self.SKIP32 = ''
        self.SHA1 = None
        self.init = 'init'
        self.STATUS = None
        self.MAGISKAPK = MAGISAPK
        self.CHROMEOS = None
        self.custom = False
        self.IS64BIT = IS64BIT
        self.PATCH_ARCH = PATCH_ARCH
        self.KEEPVERITY = KEEPVERITY
        self.KEEPFORCEENCRYPT = KEEPFORCEENCRYPT
        self.RECOVERYMODE = RECOVERYMODE
        self.Magisk_dir = Magisk_dir
        self.magiskboot = os.path.join(local, 'bin', platform.system(), platform.machine(), 'magiskboot')
        self.boot_img = boot_img

    def auto_patch(self):
        yecho("Magisk Boot Patcher By ColdWindScholar(3590361911@qq.com)")
        if self.boot_img == os.path.join(local, 'new-boot.img'):
            LOGW("Warn:Cannot be named after the generated file name")
            LOGW(f'Please Rename {self.boot_img}')
            sys.exit(1)
        if not os.path.exists(self.boot_img) or not os.path.exists(
                self.magiskboot + (".exe" if os.name == 'nt' else '')):
            LOGE("Cannot Found Boot.img or Not Support Your Device")
            sys.exit(1)
        if self.MAGISKAPK:
            self.extract_magisk()
        self.unpack()
        self.check()
        self.patch()
        self.patch_kernel()
        self.repack()
        self.cleanup()

    def exec(self, *args, out=0):
        full = [self.magiskboot, *args]
        conf = subprocess.CREATE_NO_WINDOW if os.name != 'posix' else 0
        try:
            ret = subprocess.Popen(full, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, creationflags=conf)
            for i in iter(ret.stdout.readline, b""):
                if out == 0:
                    print(i.decode("utf-8", "ignore").strip())
        except subprocess.CalledProcessError as e:
            ret = None
            ret.wait = self.error
            ret.returncode = 1
            for i in iter(e.stdout.readline, b""):
                if out == 0:
                    print(i.decode("utf-8", "ignore").strip())
        ret.wait()
        return ret.returncode

    def unpack(self):
        ret = self.exec('unpack', self.boot_img)
        if ret == 1:
            LOGW('! Unsupported/Unknown image format')
            sys.exit(1)
        elif ret == 2:
            yecho('- ChromeOS boot image detected')
            LOGW('ChromeOS not support yet')
            self.CHROMEOS = True
            sys.exit(1)
        elif ret != 0:
            LOGW('! Unable to unpack boot image')
            sys.exit(1)
        if os.path.exists(os.path.join(local, 'recovery_dtbo')):
            self.RECOVERYMODE = True

    def check(self):
        yecho('- Checking ramdisk status')
        self.STATUS = self.exec('cpio', 'ramdisk.cpio', 'test') if os.path.exists(os.path.join(local, 'ramdisk.cpio')) else 0
        if (self.STATUS & 3) == 0:
            yecho("- Stock boot image detected")
            self.SHA1 = self.sha1(self.boot_img)
            shutil.copyfile(self.boot_img, os.path.join(local, 'stock_boot.img'))
            shutil.copyfile(os.path.join(local, 'ramdisk.cpio'), os.path.join(local, 'ramdisk.cpio.orig')) if os.path.exists(os.path.join(local, 'ramdisk.cpio')) else self.SKIPBACKUP = '#'
        elif (self.STATUS & 3) == 1:
            yecho("- Magisk patched boot image detected")
            if not self.SHA1:
                self.SHA1 = self.sha1(os.path.join(local, 'ramdisk.cpio'))
            self.exec('cpio', 'ramdisk.cpio', 'restore')
            shutil.copyfile(os.path.join(local, 'ramdisk.cpio'), os.path.join(local, 'ramdisk.cpio.orig'))
            self.remove(os.path.join(local, 'stock_boot.img'))
        elif (self.STATUS & 3) == 2:
            LOGW("! Boot image patched by unsupported programs")
            LOGW("! Please restore back to stock boot image")
            sys.exit(1)
        if not (self.STATUS & 4) == 0:
            # AFFGGH: For Sony
            self.init = 'init.real'

    def patch(self):
        yecho("- Patching ramdisk")
        with open(os.path.join(local, 'config'), 'w', encoding='utf-8', newline='\n') as config:
            config.write(f'KEEPVERITY={self.KEEPVERITY}\n')
            config.write(f'KEEPFORCEENCRYPT={self.KEEPFORCEENCRYPT}\n')
            config.write(f'RECOVERYMODE={self.RECOVERYMODE}\n')
            if self.SHA1:
                config.write(f'SHA1={self.SHA1}')
        self.SKIP64 = '' if self.IS64BIT else '#'
        self.exec('compress=xz', os.path.join(self.Magisk_dir, "magisk32"), 'magisk32.xz') if os.path.exists(os.path.join(self.Magisk_dir, "magisk32")) else self.SKIP32 = '#'
        self.exec('compress=xz', os.path.join(self.Magisk_dir, "magisk64"), 'magisk64.xz') if os.path.exists(os.path.join(self.Magisk_dir, "magisk64")) else self.SKIP64 = '#'
        self.exec('compress=xz', os.path.join(self.Magisk_dir, "stub.apk"), 'stub.xz') if os.path.exists(os.path.join(self.Magisk_dir, "stub.apk")) else self.SKIPSTUB = '#'
        self.exec('cpio', 'ramdisk.cpio',
                  f"add 0750 {self.init} {os.path.join(self.Magisk_dir, 'magiskinit')}",
                  "mkdir 0750 overlay.d",
                  "mkdir 0750 overlay.d/sbin",
                  f"{self.SKIP32} add 0644 overlay.d/sbin/magisk32.xz magisk32.xz",
                  f"{self.SKIP64} add 0644 overlay.d/sbin/magisk64.xz magisk64.xz",
                  f"{self.SKIPSTUB} add 0644 overlay.d/sbin/stub.xz stub.xz",
                  'patch',
                  f"{self.SKIPBACKUP} backup ramdisk.cpio.orig",
                  "mkdir 000 .backup",
                  "add 000 .backup/.magisk config"
                  )
        for w in ['ramdisk.cpio.orig', 'config', 'magisk32.xz', 'magisk64.xz']:
            self.remove(os.path.join(local, w))
        for dt in ['dtb', 'kernel_dtb', 'extra']:
            if os.path.exists(os.path.join(local, dt)):
                print(f"- Patch fstab in {dt}")
                self.exec('dtb', dt, 'patch')

    @staticmethod
    def remove(file_):
        if os.path.exists(os.path.join(local, file_)):
            if os.path.isdir(os.path.join(local, file_)):
                shutil.rmtree(file_)
            elif os.path.isfile(os.path.join(local, file_)):
                os.remove(os.path.join(local, file_))

    def patch_kernel(self):
        if os.path.exists(os.path.join(local, 'kernel')):
            self.exec('hexpatch', 'kernel',
                      '49010054011440B93FA00F71E9000054010840B93FA00F7189000054001840B91FA00F7188010054',
                      'A1020054011440B93FA00F7140020054010840B93FA00F71E0010054001840B91FA00F7181010054')
            self.exec('hexpatch', 'kernel', '821B8012', 'E2FF8F12')
            self.exec('hexpatch', 'kernel', '736B69705F696E697472616D667300', '77616E745F696E697472616D667300')

    def repack(self):
        yecho("- Repacking boot image")
        if self.exec('repack', self.boot_img) != 0:
            LOGW("! Unable to repack boot image")

    def extract_magisk(self):
        custom = os.path.join(local, 'custom')
        if os.path.exists(custom):
            shutil.rmtree(custom)
        lib_library = {'libmagisk64.so': 'magisk64', 'libmagisk32.so': 'magisk32', 'libmagiskinit.so': 'magiskinit'}
        if not os.path.exists(custom):
            os.makedirs(custom)
        if not os.path.exists(self.MAGISKAPK):
            LOGE(f"We cannot Found {self.MAGISKAPK}, Please Check path!!!")
            LOGE(f"Use default binary to patch!")
            return
        else:
            if not zipfile.is_zipfile(self.MAGISKAPK):
                LOGE(f"{self.MAGISKAPK} Not apk!!!")
                return
            else:
                with zipfile.ZipFile(self.MAGISKAPK) as ma:
                    namelist = ma.namelist()
                    arch = [i.split('/')[1].strip() for i in namelist if
                            i.startswith('lib') and i.endswith('libmagiskboot.so')]
                    num_arch = {str(num): i for num, i in enumerate(arch)}
                    if not self.PATCH_ARCH:
                        print("Which Arch You Want To Patch?")
                        for n in num_arch:
                            print(f'[{n}]--{num_arch[n]}')
                        var = input('Please Select:')
                        if var in num_arch.keys():
                            patch_archs = [i for i in arch if num_arch[var][:3] in i]
                        else:
                            LOGE(f"{var} Cannot Found. Please Choose A Correct Choice!")
                            sys.exit(1)
                    else:
                        var = self.PATCH_ARCH
                        if var in arch:
                            patch_archs = [i for i in arch if var[:3] in i]
                        else:
                            LOGE(f"{var} Cannot Found. Please Choose A Correct Choice!")
                            sys.exit(1)
                    for patch_arch in patch_archs:
                        for i in [i for i in namelist if
                                  patch_arch in i and os.path.basename(i).startswith('libmagisk')]:
                            if os.path.basename(i) in ['libmagiskboot.so', 'libmagiskpolicy.so']:
                                continue
                            ma.extract(i, custom)
                            dst = os.path.join(custom, os.path.basename(i))
                            if os.path.exists(dst):
                                if os.path.getsize(os.path.join(custom, i)) > os.path.getsize(dst):
                                    shutil.copyfile(os.path.join(custom, i), dst)
                            else:
                                shutil.copyfile(os.path.join(custom, i), dst)
                    if 'assets/stub.apk' in namelist:
                        ma.extract('assets/stub.apk', path=custom)
                        shutil.copyfile(os.path.join(custom, 'assets/stub.apk'), (os.path.join(custom, 'stub.apk')))
                    shutil.rmtree(os.path.join(custom, 'lib'))
                    shutil.rmtree(os.path.join(custom, 'assets'))
                    for i in os.listdir(custom):
                        if os.path.isfile(os.path.join(custom, i)):
                            if os.path.basename(i) in lib_library.keys():
                                shutil.move(os.path.join(custom, i),
                                            os.path.join(custom, lib_library[os.path.basename(i)]))
                self.Magisk_dir = custom
                self.custom = True

    def cleanup(self):
        if self.custom:
            shutil.rmtree(self.Magisk_dir)
        for w in ['kernel', 'kernel_dtb', 'ramdisk.cpio', 'stub.xz', 'stock_boot.img', 'dtb']:
            if os.path.exists(os.path.join(local, w)):
                self.remove(os.path.join(local, w))
        LOGS(f"Done! Out:{os.path.join(local, 'new-boot.img')}")

    def get_arch(self):
        with zipfile.ZipFile(self.MAGISKAPK) as ma:
            return [i.split('/')[1].strip() for i in ma.namelist() if
                    i.startswith('lib') and i.endswith('libmagiskboot.so')]

    @staticmethod
    def error(code=1):
        LOGE(f"Error: {code}")
        sys.exit(code)

    @staticmethod
    def sha1(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return hashlib.sha1(f.read()).hexdigest()
        else:
            return ''
