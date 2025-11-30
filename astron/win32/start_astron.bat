@echo off
setlocal
pushd "%~dp0.."
title Pirates Online Rewritten - Astron Cluster

rem Grab users prefered config file
set /P ASTRON_CONFIG=Config File (DEFAULT: astrond): || ^
set ASTRON_CONFIG=astrond

echo ====================================
echo Starting Pirates Online Rewritten...
echo Config: %ASTRON_CONFIG%
echo ====================================

:main
"%~dp0astrond.exe" --loglevel debug "config/%ASTRON_CONFIG%.yml"
goto main
