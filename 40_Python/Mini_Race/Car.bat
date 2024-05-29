@echo off

set python3=python

if exist "C:\TCC\Tools\python3\3.7.4-29_WIN64_2" set "python3=C:\TCC\Tools\python3\3.7.4-29_WIN64_2\python.exe"
if exist "D:\Program Files\Python36" set "python3=D:\Program Files\Python36\python.exe"

"%python3%" Car.py

pause