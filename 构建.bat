@echo off
pipreqs . --encoding=utf8 --force
pyinstaller -F -c --icon="icon.png" .\��ǰ��װԭ��Ԥ���ذ�.py
copy hpatchz.exe ./dist/
pause