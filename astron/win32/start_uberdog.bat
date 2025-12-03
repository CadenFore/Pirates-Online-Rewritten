@echo off
setlocal
pushd "%~dp0..\\.."
title Pirates Online Rewritten - UberDOG

rem Choose correct python command to execute the game
set PYTHON_CMD=ppython

echo ============================================
echo Starting Pirates Online Rewritten UberDOG...
echo PPython: %PYTHON_CMD%
echo ============================================

rem Start UberDOG server (single run; keep window open on exit)
%PYTHON_CMD% -m pirates.uberdog.ServiceStart 
pause
