@echo off
set var = 0
rem ** �ô����ɡ�kangour Aronld�����ף�����������ʹ�úʹ�����Ȩ�������뱣���˲�������������
rem ** ʹ�ñ�����ǰ����ȷ��.py�ļ���.bat�ļ�������һ�¡�
rem ** ���磬�����á�love�����ļ���������ôֻ�е�bat�ļ���Ϊ��love.bat��py�ļ�Ϊ��love.py��ʱ��˫��love.bat�ļ�������׼ȷִ�е�love.py����
rem ** kangour Aronld д��2017��12��4��
rem **
cls
rem ** ��ӡ��ʾ��Ϣ
@echo --- Runner %date% %time% the python result %~dp0 ---
@echo.
rem ** ��ȡ��ǰĿ¼·��
cd %~dp0
rem ** ��ȡ��ǰbat�ļ�����ǰ׺���֣�
for /f "delims=" %%i in ("%0") do set aa=%%~ni
set "aa=%aa%.py"
rem ** ����Python������ִ��
python %aa%
echo.
echo.
echo.
pause