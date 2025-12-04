@echo off
setlocal
cd /d "%~dp0.."
title Pirates Online Rewritten - Full Stack Launcher

rem Adjust these if you use a different python launcher
set PYTHON_CMD=ppython

echo ============================================
echo Launching Pirates Online Rewritten stack...
echo Using PYTHON_CMD: %PYTHON_CMD%
echo ============================================

rem Start Astron (Message Director) in its own window
start "POR - Astron" /D "%cd%\astron" cmd /c "win32\astrond.exe --loglevel debug config/astrond.yml"

rem Start UberDOG in its own window
start "POR - UberDOG" /D "%cd%" cmd /c "%PYTHON_CMD% -m pirates.uberdog.ServiceStart & pause"

rem Start AI shard in its own window
start "POR - AI" /D "%cd%" cmd /c "%PYTHON_CMD% -m pirates.ai.ServiceStart --base-channel 401000000 --district-name DevHaven & pause"

rem Small delay before launching the client so the backends are up
timeout /t 2 /nobreak >nul

rem Start client in its own window (uses start_client.bat prompts)
start "POR - Client" /D "%cd%\win32" cmd /c "start_client.bat"

echo All processes launched. Keep their windows open.
