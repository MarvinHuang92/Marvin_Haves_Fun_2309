@echo off
set python3="D:\Program Files\Python3133\python.exe"

@REM 安装依赖库
@REM %python3% -m pip install pandas
@REM %python3% -m pip install numpy
@REM %python3% -m pip install matplotlib
@REM %python3% -m pip install yfinance

@REM 运行
%python3% trader.py

pause