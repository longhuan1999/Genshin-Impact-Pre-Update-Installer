@echo off
pipreqs . --encoding=utf8 --force
pyinstaller -F -c --icon="icon.png" .\ԭ��Ԥ���°�װ����.py
copy .\dist\ԭ��Ԥ���°�װ����.exe .\release\ԭ��Ԥ���°�װ����\
copy .\dist\ԭ��Ԥ���°�װ����.exe .\
pause