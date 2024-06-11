@echo off
call config.bat
gcc.exe -g %filename%.cpp -o %filename%.exe -lstdc++
call %filename%.exe
pause