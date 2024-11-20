@echo off

set "python_3_root=C:\TCC\Tools\python3\3.7.4-29_WIN64_2"

REM pushd %python_3_root%
REM python.exe -m pip install pyautogui
REM popd

%python_3_root%\python.exe img_merge.py

pause