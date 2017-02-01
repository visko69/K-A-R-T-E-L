@echo off
title Red Discord Bot - Windows Launcher
color 0F ::Replace with 0C for the Red experience

echo Please wait
chcp 65001 > NUL

echo.
mode con: cols=80 lines=12
pushd %~dp0

::Attempts to start py launcher without relying on PATH
%SYSTEMROOT%\py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO attempt
%SYSTEMROOT%\py.exe -3.5 launcher.py
IF %ERRORLEVEL% NEQ 0 goto attempt
PAUSE
GOTO end

:preattempt

::Attempts to start py launcher by relying on PATH
:attempt
py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO lastattempt
py.exe -3 launcher.py
PAUSE
GOTO end

::As a last resort, attempts to start whatever Python there is
:lastattempt
python.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO message
python.exe launcher.py
PAUSE
GOTO end

:message
cks
echo( Couldn't find a valid Python ^>3.5 installation. Python needs to be installed and available in the PATH environment
echo( variable.
echo( Please visit https://twentysix26.github.io/Red-Docs/red_win_requirements/#software
echo(
echo( Press any key to exit
pause > NUL
goto message

:end
exit
