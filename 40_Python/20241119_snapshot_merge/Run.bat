@echo off

@REM set "python_3_root=C:\TCC\Tools\python3\3.7.4-29_WIN64_2"
set "python_3_root=D:\Program Files\Python38"

@REM pushd %python_3_root%
@REM python.exe -m pip install pyautogui
@REM python.exe -m pip install pynput
@REM python.exe -m pip install numpy
@REM popd

@REM 批量裁剪图片
"%python_3_root%\python.exe" img_crop.py

@REM 批量拼合图片
"%python_3_root%\python.exe" img_merge.py

pause