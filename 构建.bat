@echo off
pipreqs . --encoding=utf8 --force
pyinstaller -F -c --icon="icon.png" .\提前安装原神预下载包.py
copy hpatchz.exe ./dist/
pause