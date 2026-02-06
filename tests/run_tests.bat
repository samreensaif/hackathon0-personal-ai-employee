@echo off
REM ============================================================================
REM Test Runner Script for Gmail MCP Server (Windows)
REM
REM This script provides convenient commands for running different test suites.
REM
REM Usage:
REM   tests\run_tests.bat [command] [options]
REM
REM Commands:
REM   all           - Run all mock tests
REM   integration   - Run integration tests
REM   coverage      - Run with coverage report
REM   quick         - Run quick tests only
REM   failed        - Re-run failed tests
REM   specific      - Run specific test
REM   clean         - Clean test artifacts
REM ============================================================================

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

REM Colors (Windows 10+)
for /F %%A in ('echo prompt $E^| cmd') do set "ESC=%%A"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM Parse command
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=all"
shift

REM Check if pytest is installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo %RED%[ERROR]%NC% pytest not found. Installing dependencies...
    pip install -r tests\requirements.txt
)

REM Execute command
if /i "%COMMAND%"=="all" goto cmd_all
if /i "%COMMAND%"=="integration" goto cmd_integration
if /i "%COMMAND%"=="coverage" goto cmd_coverage
if /i "%COMMAND%"=="quick" goto cmd_quick
if /i "%COMMAND%"=="failed" goto cmd_failed
if /i "%COMMAND%"=="specific" goto cmd_specific
if /i "%COMMAND%"=="clean" goto cmd_clean
if /i "%COMMAND%"=="help" goto show_usage
if /i "%COMMAND%"=="--help" goto show_usage
if /i "%COMMAND%"=="-h" goto show_usage

echo %RED%[ERROR]%NC% Unknown command: %COMMAND%
echo.
goto show_usage

REM ============================================================================
REM Commands
REM ============================================================================

:cmd_all
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Running All Mock Tests%NC%
    echo %BLUE%===========================================%NC%
    echo.
    pytest tests\test_email_mcp.py -v %*
    goto end

:cmd_integration
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Running Integration Tests%NC%
    echo %BLUE%===========================================%NC%
    echo.
    echo %YELLOW%[INFO]%NC% This requires real Gmail API access
    pytest tests\test_email_mcp.py -v --run-integration %*
    goto end

:cmd_coverage
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Running Tests with Coverage%NC%
    echo %BLUE%===========================================%NC%
    echo.
    pytest tests\test_email_mcp.py -v ^
        --cov=mcp_servers\email ^
        --cov-report=html ^
        --cov-report=term-missing ^
        %*
    echo.
    echo %GREEN%[OK]%NC% Coverage report: htmlcov\index.html
    goto end

:cmd_quick
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Running Quick Tests%NC%
    echo %BLUE%===========================================%NC%
    echo.
    pytest tests\test_email_mcp.py -v -m "not slow" %*
    goto end

:cmd_failed
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Re-running Failed Tests%NC%
    echo %BLUE%===========================================%NC%
    echo.
    pytest tests\test_email_mcp.py -v --lf %*
    goto end

:cmd_specific
    if "%~2"=="" (
        echo %RED%[ERROR]%NC% Please specify test name
        echo Example: tests\run_tests.bat specific TestDraftEmail::test_draft_email_success
        goto end
    )
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Running Specific Test: %~2%NC%
    echo %BLUE%===========================================%NC%
    echo.
    pytest "tests\test_email_mcp.py::%~2" -v
    goto end

:cmd_clean
    echo.
    echo %BLUE%===========================================%NC%
    echo %BLUE%Cleaning Test Artifacts%NC%
    echo %BLUE%===========================================%NC%
    echo.

    if exist "htmlcov" rmdir /s /q "htmlcov"
    if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
    if exist ".coverage" del /f /q ".coverage"
    if exist "tests\__pycache__" rmdir /s /q "tests\__pycache__"

    echo %GREEN%[OK]%NC% Test artifacts cleaned
    goto end

:show_usage
    echo.
    echo %BLUE%Gmail MCP Server Test Runner%NC%
    echo.
    echo %YELLOW%USAGE:%NC%
    echo     %~nx0 [COMMAND] [OPTIONS]
    echo.
    echo %YELLOW%COMMANDS:%NC%
    echo     all           Run all mock tests
    echo     integration   Run integration tests
    echo     coverage      Run with coverage report
    echo     quick         Run quick tests only
    echo     failed        Re-run failed tests
    echo     specific      Run specific test
    echo     clean         Clean test artifacts
    echo     help          Show this help
    echo.
    echo %YELLOW%OPTIONS:%NC%
    echo     -v            Verbose output
    echo     -s            Show print statements
    echo     -x            Stop on first failure
    echo     -k EXPR       Run tests matching expression
    echo     --pdb         Drop into debugger on failure
    echo.
    echo %YELLOW%EXAMPLES:%NC%
    echo     %~nx0 all
    echo     %~nx0 integration
    echo     %~nx0 coverage
    echo     %~nx0 specific TestDraftEmail::test_draft_email_success
    echo     %~nx0 quick
    echo     %~nx0 failed
    echo     %~nx0 clean
    echo.
    goto end

:end
    exit /b 0
