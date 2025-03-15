@echo off

@REM set "python_3_root=C:\TCC\Tools\python3\3.7.4-29_WIN64_2"
set "python_3_root=D:\Program Files\Python38"

@REM pushd %python_3_root%
@REM python.exe -m pip install pyautogui
@REM python.exe -m pip install pynput
@REM python.exe -m pip install numpy
@REM popd

:Get_user_input
echo # Please choose a job type #
echo 1. Rotate images
echo 2. Crop images
echo 3. Merge images
set /p "user_input=Your choice: "
echo.

if %user_input%==1 (
    set "py_script=img_rotate.py"
) else if %user_input%==2 (
    set "py_script=img_crop.py"
) else if %user_input%==3 (
    set "py_script=img_merge.py"
) else (
    goto Get_user_input
)

call "%python_3_root%\python.exe" %py_script%

pause