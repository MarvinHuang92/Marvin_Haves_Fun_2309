@echo off
call config_home.bat
gcc.exe -g %filename%.cpp -o %filename%.exe -lstdc++
pause