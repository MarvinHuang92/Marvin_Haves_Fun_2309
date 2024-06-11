set filename=sizeOfStruct

REM working PC
set "mingw_path_1=C:\TCC\Tools\mingw64\8.1.0_WIN64\bin"
if exist %mingw_path_1% set PATH=%PATH%;%mingw_path_1%

REM home PC
set "mingw_path_2=D:\Programming\Cmake\MinGW\bin"
if exist %mingw_path_2% set PATH=%PATH%;%mingw_path_2%