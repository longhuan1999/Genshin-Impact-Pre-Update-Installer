@echo off
pipreqs . --encoding=utf8 --force
pyinstaller -F -c --icon="icon.png" .\原神预更新安装程序.py
copy .\dist\原神预更新安装程序.exe .\release\原神预更新安装程序\
copy .\dist\原神预更新安装程序.exe .\
pause