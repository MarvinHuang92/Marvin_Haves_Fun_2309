@echo off

@REM GIGABYTE
if exist "D:\Program Files\Python36" set python3="D:\Program Files\Python36\python.exe"

@REM SURFACE
if exist "D:\Program Files\Python39" set python3="D:\Program Files\Python36\python.exe"

%python3% main.py

pause