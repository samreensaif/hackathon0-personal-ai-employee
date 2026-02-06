@echo off
REM ============================================================================
REM MCP Servers Startup Script (Windows)
REM
REM This script starts all MCP servers in the background, monitors their health,
REM and provides status reporting with colored output.
REM
REM Usage:
REM   scripts\start_mcp_servers.bat [start|stop|status|restart]
REM
REM Requirements:
REM   - Node.js (for Gmail server)
REM   - Windows 10+ (for colored output support)
REM
REM Logs:
REM   - mcp_servers\logs\YYYY-MM-DD.log
REM   - Individual server logs in mcp_servers\logs\[server-name].log
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM ============================================================================
REM CONFIGURATION
REM ============================================================================

REM Get script directory and project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

REM Log directory
set "LOG_DIR=%PROJECT_ROOT%\mcp_servers\logs"
set "PID_DIR=%LOG_DIR%\pids"

REM Get current date for log file
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set "TIMESTAMP=%%c-%%a-%%b"
)
set "MAIN_LOG=%LOG_DIR%\%TIMESTAMP%.log"

REM Colors (Windows 10+ ANSI escape codes)
REM Enable ANSI escape sequences
for /F %%A in ('echo prompt $E^| cmd') do set "ESC=%%A"
set "RED=%ESC%[31m"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "MAGENTA=%ESC%[35m"
set "CYAN=%ESC%[36m"
set "NC=%ESC%[0m"
set "BOLD=%ESC%[1m"

REM Server configurations
REM Format: SERVER_NAME=command
set "SERVER_gmail=node mcp_servers\email\server.js"

REM ============================================================================
REM HELPER FUNCTIONS
REM ============================================================================

:print_color
    echo %~1%~2%NC%
    exit /b 0

:print_header
    echo.
    echo %CYAN%==========================================%NC%
    echo %CYAN%%~1%NC%
    echo %CYAN%==========================================%NC%
    echo.
    exit /b 0

:print_success
    echo %GREEN%[OK] %~1%NC%
    exit /b 0

:print_error
    echo %RED%[ERROR] %~1%NC%
    exit /b 0

:print_warning
    echo %YELLOW%[WARN] %~1%NC%
    exit /b 0

:print_info
    echo %BLUE%[INFO] %~1%NC%
    exit /b 0

:log_message
    REM Get current timestamp
    for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do (
        set "HOUR=%%a"
        set "MIN=%%b"
        set "SEC=%%c"
    )
    set "HOUR=%HOUR: =0%"
    echo [%DATE% %HOUR%:%MIN%:%SEC%] [%~1] %~2 >> "%MAIN_LOG%"
    exit /b 0

:ensure_directories
    if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
    if not exist "%PID_DIR%" mkdir "%PID_DIR%"
    if not exist "%MAIN_LOG%" type nul > "%MAIN_LOG%"
    call :log_message "INFO" "Directories initialized"
    exit /b 0

:is_process_running
    REM Check if PID is running
    set "PID=%~1"
    tasklist /FI "PID eq %PID%" 2>nul | find "%PID%" >nul
    exit /b %ERRORLEVEL%

:get_server_pid
    set "SERVER_NAME=%~1"
    set "PID_FILE=%PID_DIR%\%SERVER_NAME%.pid"
    set "SERVER_PID="

    if exist "%PID_FILE%" (
        set /p SERVER_PID=<"%PID_FILE%"
    )

    exit /b 0

:is_server_running
    set "SERVER_NAME=%~1"
    call :get_server_pid "%SERVER_NAME%"

    if "%SERVER_PID%"=="" (
        exit /b 1
    )

    call :is_process_running "%SERVER_PID%"
    exit /b %ERRORLEVEL%

:start_server
    set "SERVER_NAME=%~1"
    set "COMMAND=!SERVER_%SERVER_NAME%!"
    set "PID_FILE=%PID_DIR%\%SERVER_NAME%.pid"
    set "LOG_FILE=%LOG_DIR%\%SERVER_NAME%.log"

    call :print_info "Starting %SERVER_NAME%..."
    call :log_message "INFO" "Starting server: %SERVER_NAME%"

    REM Check if already running
    call :is_server_running "%SERVER_NAME%"
    if %ERRORLEVEL% equ 0 (
        call :get_server_pid "%SERVER_NAME%"
        call :print_warning "%SERVER_NAME% is already running (PID: !SERVER_PID!)"
        call :log_message "WARN" "%SERVER_NAME% already running"
        exit /b 0
    )

    REM Start the server in background
    start /B "" cmd /c "%COMMAND% >> "%LOG_FILE%" 2>&1"

    REM Get the PID (Windows doesn't make this easy, using WMIC)
    timeout /t 1 /nobreak >nul

    REM Find the most recent node.exe process (assuming it's our server)
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq node.exe" ^| find "node.exe"') do (
        set "NEW_PID=%%a"
        goto :found_pid
    )

    :found_pid
    if not defined NEW_PID (
        call :print_error "%SERVER_NAME% failed to start"
        call :log_message "ERROR" "%SERVER_NAME% failed to start"
        exit /b 1
    )

    REM Save PID
    echo !NEW_PID!>"%PID_FILE%"

    REM Wait and verify
    timeout /t 2 /nobreak >nul

    call :is_process_running "!NEW_PID!"
    if %ERRORLEVEL% equ 0 (
        call :print_success "%SERVER_NAME% started successfully (PID: !NEW_PID!)"
        call :log_message "INFO" "%SERVER_NAME% started with PID: !NEW_PID!"
        exit /b 0
    ) else (
        call :print_error "%SERVER_NAME% failed to start"
        call :log_message "ERROR" "%SERVER_NAME% failed to start"

        REM Show last few lines of log
        if exist "%LOG_FILE%" (
            call :print_error "Last 5 lines of log:"
            powershell -Command "Get-Content '%LOG_FILE%' -Tail 5 | ForEach-Object { Write-Host '  ' $_ }"
        )

        del /f /q "%PID_FILE%" 2>nul
        exit /b 1
    )

:stop_server
    set "SERVER_NAME=%~1"
    call :get_server_pid "%SERVER_NAME%"
    set "PID_FILE=%PID_DIR%\%SERVER_NAME%.pid"

    call :print_info "Stopping %SERVER_NAME%..."
    call :log_message "INFO" "Stopping server: %SERVER_NAME%"

    if "%SERVER_PID%"=="" (
        call :print_warning "%SERVER_NAME% is not running (no PID file)"
        exit /b 0
    )

    call :is_process_running "%SERVER_PID%"
    if %ERRORLEVEL% neq 0 (
        call :print_warning "%SERVER_NAME% is not running (stale PID)"
        del /f /q "%PID_FILE%" 2>nul
        exit /b 0
    )

    REM Try graceful shutdown
    taskkill /PID %SERVER_PID% >nul 2>&1

    REM Wait up to 10 seconds
    set "COUNT=0"
    :wait_loop
    call :is_process_running "%SERVER_PID%"
    if %ERRORLEVEL% neq 0 goto :stopped
    if %COUNT% geq 10 goto :force_kill
    timeout /t 1 /nobreak >nul
    set /a COUNT+=1
    goto :wait_loop

    :force_kill
    call :print_warning "Forcing shutdown of %SERVER_NAME%..."
    taskkill /F /PID %SERVER_PID% >nul 2>&1
    timeout /t 1 /nobreak >nul

    :stopped
    call :is_process_running "%SERVER_PID%"
    if %ERRORLEVEL% neq 0 (
        call :print_success "%SERVER_NAME% stopped"
        call :log_message "INFO" "%SERVER_NAME% stopped"
        del /f /q "%PID_FILE%" 2>nul
        exit /b 0
    ) else (
        call :print_error "Failed to stop %SERVER_NAME%"
        call :log_message "ERROR" "Failed to stop %SERVER_NAME%"
        exit /b 1
    )

:get_server_status
    set "SERVER_NAME=%~1"
    call :get_server_pid "%SERVER_NAME%"

    REM Format output
    set "STATUS_LINE=  %-15s %-12s %-10s"

    if "%SERVER_PID%"=="" (
        echo   %SERVER_NAME%          %RED%STOPPED%NC%     -
    ) else (
        call :is_process_running "%SERVER_PID%"
        if !ERRORLEVEL! equ 0 (
            echo   %SERVER_NAME%          %GREEN%RUNNING%NC%     !SERVER_PID!
        ) else (
            echo   %SERVER_NAME%          %YELLOW%CRASHED%NC%     !SERVER_PID! (stale^)
        )
    )
    exit /b 0

REM ============================================================================
REM MAIN COMMANDS
REM ============================================================================

:cmd_start
    call :print_header "Starting MCP Servers"
    call :ensure_directories

    set "FAILED=0"

    REM Start gmail server
    call :start_server "gmail"
    if %ERRORLEVEL% neq 0 set /a FAILED+=1

    echo.

    if %FAILED% equ 0 (
        call :print_success "All servers started successfully"
        call :log_message "INFO" "All servers started"
    ) else (
        call :print_error "%FAILED% server(s) failed to start"
        call :log_message "ERROR" "%FAILED% servers failed to start"
    )
    exit /b 0

:cmd_stop
    call :print_header "Stopping MCP Servers"

    set "FAILED=0"

    REM Stop gmail server
    call :stop_server "gmail"
    if %ERRORLEVEL% neq 0 set /a FAILED+=1

    echo.

    if %FAILED% equ 0 (
        call :print_success "All servers stopped"
        call :log_message "INFO" "All servers stopped"
    ) else (
        call :print_error "%FAILED% server(s) failed to stop"
        call :log_message "ERROR" "%FAILED% servers failed to stop"
    )
    exit /b 0

:cmd_status
    call :print_header "MCP Servers Status"

    echo   %BOLD%SERVER          STATUS       PID%NC%
    echo   %CYAN%--------------------------------------------------------------%NC%

    REM Show gmail server status
    call :get_server_status "gmail"

    echo.
    call :print_info "Logs:"
    echo   Main log: %MAIN_LOG%
    echo   gmail: %LOG_DIR%\gmail.log
    echo.
    exit /b 0

:cmd_restart
    call :print_header "Restarting MCP Servers"
    call :cmd_stop
    timeout /t 2 /nobreak >nul
    call :cmd_start
    exit /b 0

:cmd_health
    call :print_header "Health Check"

    set "UNHEALTHY=0"

    REM Check gmail server
    echo   Checking gmail...
    call :is_server_running "gmail"
    if %ERRORLEVEL% equ 0 (
        call :print_success "Healthy"
    ) else (
        call :print_error "Unhealthy"
        set /a UNHEALTHY+=1
    )

    echo.
    if %UNHEALTHY% equ 0 (
        call :print_success "All servers healthy"
    ) else (
        call :print_error "%UNHEALTHY% server(s) unhealthy"
    )
    exit /b 0

:cmd_logs
    set "SERVER_NAME=%~1"

    if "%SERVER_NAME%"=="" (
        call :print_info "Showing main log (last 50 lines):"
        echo.
        powershell -Command "Get-Content '%MAIN_LOG%' -Tail 50"
    ) else (
        set "LOG_FILE=%LOG_DIR%\%SERVER_NAME%.log"
        if exist "!LOG_FILE!" (
            call :print_info "Showing %SERVER_NAME% log (last 50 lines):"
            echo.
            powershell -Command "Get-Content '!LOG_FILE!' -Tail 50"
        ) else (
            call :print_error "Log file not found: !LOG_FILE!"
        )
    )
    exit /b 0

:show_usage
    echo.
    echo %BOLD%MCP Servers Management Script%NC%
    echo.
    echo %BOLD%USAGE:%NC%
    echo     %~nx0 [COMMAND] [OPTIONS]
    echo.
    echo %BOLD%COMMANDS:%NC%
    echo     start       Start all MCP servers
    echo     stop        Stop all MCP servers
    echo     restart     Restart all MCP servers
    echo     status      Show status of all servers
    echo     health      Run health checks on all servers
    echo     logs [name] Show logs (all or specific server)
    echo     help        Show this help message
    echo.
    echo %BOLD%EXAMPLES:%NC%
    echo     %~nx0 start              # Start all servers
    echo     %~nx0 stop               # Stop all servers
    echo     %~nx0 status             # Show server status
    echo     %~nx0 logs gmail         # Show gmail server logs
    echo.
    echo %BOLD%LOG FILES:%NC%
    echo     Main log:     %MAIN_LOG%
    echo     Server logs:  %LOG_DIR%\[server-name].log
    echo     PID files:    %PID_DIR%\[server-name].pid
    echo.
    echo %BOLD%SERVERS:%NC%
    echo     - gmail
    echo.
    exit /b 0

REM ============================================================================
REM MAIN ENTRY POINT
REM ============================================================================

:main
    REM Parse command
    set "COMMAND=%~1"
    if "%COMMAND%"=="" set "COMMAND=status"

    if /i "%COMMAND%"=="start" (
        call :cmd_start
    ) else if /i "%COMMAND%"=="stop" (
        call :cmd_stop
    ) else if /i "%COMMAND%"=="restart" (
        call :cmd_restart
    ) else if /i "%COMMAND%"=="status" (
        call :cmd_status
    ) else if /i "%COMMAND%"=="health" (
        call :cmd_health
    ) else if /i "%COMMAND%"=="logs" (
        call :cmd_logs "%~2"
    ) else if /i "%COMMAND%"=="help" (
        call :show_usage
    ) else if /i "%COMMAND%"=="--help" (
        call :show_usage
    ) else if /i "%COMMAND%"=="-h" (
        call :show_usage
    ) else (
        call :print_error "Unknown command: %COMMAND%"
        echo.
        call :show_usage
        exit /b 1
    )

    exit /b 0

REM Run main
call :main %*
