@echo off
if exist C:\TCC\Tools\python3\3.7.4-29_WIN64_2 (
    C:\TCC\Tools\python3\3.7.4-29_WIN64_2\python.exe Car.py
) else (
    python Car.py
)

pause