import os
import platform
import shutil
import zipfile


print(f'Build for {platform.system()}')
from pip._internal.cli.main import main as _main
_main(['install', 'pyinstaller'])
local = os.getcwd()
if platform.system() == 'Linux':
    name = 'Magisk_Patch-linux.zip'
else:
    name = 'Magisk_Patch-win.zip'


def zip_folder(folder_path):
    # 获取文件夹的绝对路径和文件夹名称
    abs_folder_path = os.path.abspath(folder_path)

    # 创建一个同名的zip文件
    zip_file_path = os.path.join(local, name)
    archive = zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED)

    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(abs_folder_path):
        for file in files:
            if file == name:
                continue
            file_path = os.path.join(root, file)
            if ".git" in file_path:
                continue
            print(f"Adding: {file_path}")
            # 将文件添加到zip文件中
            archive.write(file_path, os.path.relpath(file_path, abs_folder_path))

    # 关闭zip文件
    archive.close()
    print(f"Done!")


import PyInstaller.__main__

PyInstaller.__main__.run(['-F', 'patch.py', '--exclude-module=numpy'])

if os.name == 'nt':
    if os.path.exists(local + os.sep + "dist" + os.sep + "patch.exe"):
        shutil.move(local + os.sep + "dist" + os.sep + "patch.exe", local)
    if os.path.exists(local + os.sep + "bin" + os.sep + "Linux"):
        shutil.rmtree(local + os.sep + "bin" + os.sep + "Linux")
elif os.name == 'posix':
    if os.path.exists(local + os.sep + "dist" + os.sep + "patch"):
        shutil.move(local + os.sep + "dist" + os.sep + "patch", local)
    if os.path.exists(local + os.sep + "bin" + os.sep + "Windows"):
        shutil.rmtree(local + os.sep + "bin" + os.sep + "Windows")
    for i in os.listdir(local + os.sep + "bin" + os.sep + "Linux"):
        if i == platform.machine():
            continue
        shutil.rmtree(local + os.sep + "bin" + os.sep + "Linux" + os.sep + i)
for i in os.listdir(local):
    if i not in ['patch', 'patch.exe', 'bin', 'LICENSE']:
        print(f"Removing {i}")
        if os.path.isdir(local + os.sep + i):
            try:
                shutil.rmtree(local + os.sep + i)
            except Exception or OSError as e:
                print(e)
        elif os.path.isfile(local + os.sep + i):
            try:
                os.remove(local + os.sep + i)
            except Exception or OSError as e:
                print(e)
    else:
        print(i)
if os.name == 'posix':
    for root, dirs, files in os.walk(local, topdown=True):
        for i in files:
            print(f"Chmod {os.path.join(root, i)}")
            os.system(f"chmod a+x {os.path.join(root, i)}")

zip_folder(".")
