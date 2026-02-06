@echo off
REM Quick start script for Watcher Manager (Windows)
REM
REM Usage:
REM   start_watchers.bat          - Start all watchers
REM   start_watchers.bat stop     - Stop all watchers
REM   start_watchers.bat status   - Check status
REM

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo ==================================
echo AI Employee Watcher Manager
echo ==================================
echo.

cd /d %PROJECT_ROOT%

REM Parse command
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=start

if "%COMMAND%"=="start" goto start
if "%COMMAND%"=="stop" goto stop
if "%COMMAND%"=="status" goto status
if "%COMMAND%"=="config" goto config

echo [ERROR] Unknown command: %COMMAND%
echo.
echo Usage:
echo   %~nx0 [start^|stop^|status^|config]
echo.
exit /b 1

:start
echo Starting watcher manager...
echo.

REM Check if rich is installed
python -c "import rich" 2>nul
if errorlevel 1 (
    echo [WARNING] 'rich' not installed
    echo For beautiful dashboard, install with: pip install rich
    echo.
)

REM Start manager
python scripts\watcher_manager.py
goto end

:stop
echo Stopping all watchers...
python scripts\watcher_manager.py --stop
goto end

:status
echo Checking watcher status...
echo.
python scripts\watcher_manager.py --status
goto end

:config
echo Current configuration:
echo.
python scripts\watcher_manager.py --config
goto end

:end
endlocal
