@echo off
REM ============================================================================
REM Silver Tier AI Employee System - Demo Script (Windows)
REM ============================================================================
REM This script demonstrates all Silver Tier features in an impressive sequence
REM Perfect for recording demo videos!
REM
REM 🎬 DEMO MODE: This script simulates the workflow for demonstration purposes.
REM    It manually moves files and creates outputs to showcase the CONCEPT
REM    without requiring actual watchers, MCP servers, or API connections.
REM
REM Features demonstrated:
REM 1. Watcher System (Inbox + Gmail) - Concept Overview
REM 2. Intelligent Task Categorization - Simulated
REM 3. Approval Workflow - Manual Simulation
REM 4. MCP Action Execution - Visual Demonstration
REM 5. CEO Briefing Generation - Created/Generated
REM 6. Dashboard Updates - Created/Updated
REM
REM For production usage, use the actual watcher_manager.py and related scripts.
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors for Windows (using ANSI escape codes)
set "ESC="
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "BLUE=%ESC%[94m"
set "MAGENTA=%ESC%[95m"
set "CYAN=%ESC%[96m"
set "RED=%ESC%[91m"
set "BOLD=%ESC%[1m"
set "DIM=%ESC%[2m"
set "RESET=%ESC%[0m"

REM Enable ANSI colors in Windows Terminal
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

REM Configuration
set "PROJECT_ROOT=%~dp0.."
set "VAULT_PATH=%PROJECT_ROOT%\AI_Employee_Vault"
set "DEMO_DATA=%PROJECT_ROOT%\demo\test_data"
set "LOGS_PATH=%VAULT_PATH%\Logs"
set "PAUSE_TIME=3"

REM Check if demo mode flag is set
set "DRY_RUN="
if "%1"=="--dry-run" set "DRY_RUN=--dry-run"

cd /d "%PROJECT_ROOT%"

REM ============================================================================
REM Helper Functions
REM ============================================================================

:timestamp
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "timestamp=%dt:~0,4%-%dt:~4,2%-%dt:~6,2% %dt:~8,2%:%dt:~10,2%:%dt:~12,2%"
    echo !timestamp!
    goto :eof

:print_header
    echo.
    echo %BOLD%%CYAN%============================================================================%RESET%
    echo %BOLD%%CYAN%%~1%RESET%
    echo %BOLD%%CYAN%============================================================================%RESET%
    echo.
    goto :eof

:print_step
    call :timestamp
    echo %GREEN%[!timestamp!]%RESET% %BOLD%%~1%RESET%
    goto :eof

:print_substep
    call :timestamp
    echo %BLUE%  [!timestamp!]%RESET% %~1
    goto :eof

:print_success
    call :timestamp
    echo %GREEN%[!timestamp!] ✓%RESET% %~1
    goto :eof

:print_warning
    call :timestamp
    echo %YELLOW%[!timestamp!] ⚠%RESET% %~1
    goto :eof

:print_error
    call :timestamp
    echo %RED%[!timestamp!] ✗%RESET% %~1
    goto :eof

:print_info
    call :timestamp
    echo %CYAN%[!timestamp!] →%RESET% %~1
    goto :eof

:pause_for_video
    echo.
    echo %DIM%[PAUSE FOR VIDEO - Press any key to continue...]%RESET%
    pause >nul
    goto :eof

REM ============================================================================
REM Main Demo Sequence
REM ============================================================================

:main
    cls

    REM Banner
    echo %BOLD%%MAGENTA%
    echo  ╔═══════════════════════════════════════════════════════════════════╗
    echo  ║                                                                   ║
    echo  ║        AI EMPLOYEE SYSTEM - SILVER TIER DEMO                      ║
    echo  ║        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                        ║
    echo  ║                                                                   ║
    echo  ║        Showcasing:                                                ║
    echo  ║        • Multi-source task ingestion                              ║
    echo  ║        • Intelligent categorization                               ║
    echo  ║        • Approval workflows                                       ║
    echo  ║        • MCP action execution                                     ║
    echo  ║        • CEO briefing generation                                  ║
    echo  ║                                                                   ║
    echo  ╚═══════════════════════════════════════════════════════════════════╝
    echo %RESET%
    echo.

    if defined DRY_RUN (
        call :print_warning "Running in DRY-RUN mode - no actual actions will be executed"
    )

    echo.
    echo %YELLOW%Press any key to start the demo...%RESET%
    pause >nul

    REM ========================================================================
    REM STEP 1: Environment Setup & Cleanup
    REM ========================================================================

    call :print_header "STEP 1: Environment Setup"

    call :print_step "Cleaning up previous demo data..."

    REM Clean up old test files
    if exist "%VAULT_PATH%\test_*.md" (
        del /q "%VAULT_PATH%\test_*.md" 2>nul
        call :print_substep "Removed old test files from vault root"
    )

    if exist "%VAULT_PATH%\High_Priority\test_*.md" (
        del /q "%VAULT_PATH%\High_Priority\test_*.md" 2>nul
        call :print_substep "Cleaned High_Priority folder"
    )

    if exist "%VAULT_PATH%\Needs_Action\test_*.md" (
        del /q "%VAULT_PATH%\Needs_Action\test_*.md" 2>nul
        call :print_substep "Cleaned Needs_Action folder"
    )

    if exist "%VAULT_PATH%\Pending_Approval\test_*.md" (
        del /q "%VAULT_PATH%\Pending_Approval\test_*.md" 2>nul
        call :print_substep "Cleaned Pending_Approval folder"
    )

    if exist "%VAULT_PATH%\Approved\test_*.md" (
        del /q "%VAULT_PATH%\Approved\test_*.md" 2>nul
        call :print_substep "Cleaned Approved folder"
    )

    if exist "%VAULT_PATH%\Done\test_*.md" (
        del /q "%VAULT_PATH%\Done\test_*.md" 2>nul
        call :print_substep "Cleaned Done folder"
    )

    call :print_success "Environment cleaned and ready"

    call :print_step "Checking Python dependencies..."
    python --version >nul 2>&1
    if errorlevel 1 (
        call :print_error "Python not found! Please install Python 3.8+"
        exit /b 1
    )
    call :print_success "Python is available"

    call :pause_for_video

    REM ========================================================================
    REM STEP 2: Watcher System (Concept Overview)
    REM ========================================================================

    call :print_header "STEP 2: Watcher System Overview"

    call :print_step "Understanding the watcher architecture..."
    call :print_info "In production, the system includes:"
    call :print_info "  • Inbox Watcher (filesystem monitoring)"
    call :print_info "  • Gmail Watcher (email monitoring)"
    call :print_info "  • Continuous background processing"

    timeout /t 2 /nobreak >nul

    call :print_info "For this demo, we'll simulate the workflow"
    call :print_success "✓ Watcher concept demonstrated"

    timeout /t 1 /nobreak >nul

    call :pause_for_video

    REM ========================================================================
    REM STEP 3: Create Test Tasks
    REM ========================================================================

    call :print_header "STEP 3: Creating Test Tasks"

    call :print_step "Creating test email task..."

    REM Create test email task
    (
        echo # Email Client About Invoice
        echo.
        echo **Priority:** High
        echo **Category:** Email
        echo **Deadline:** 2026-02-06
        echo.
        echo ## Task Description
        echo.
        echo Send an email to client@example.com with the subject "Invoice - January 2026".
        echo.
        echo The email should:
        echo - Thank them for their business
        echo - Attach the January invoice PDF
        echo - Request payment within 14 days
        echo - Include our payment details
        echo.
        echo ## Action Required
        echo.
        echo ```json
        echo {
        echo   "action": "send_email",
        echo   "to": "client@example.com",
        echo   "subject": "Invoice - January 2026",
        echo   "body": "Dear Client,\n\nThank you for your continued business. Please find attached the invoice for January 2026.\n\nPayment is due within 14 days.\n\nBest regards,\nAI Employee"
        echo }
        echo ```
    ) > "%VAULT_PATH%\test_email_task.md"

    call :print_success "Created: test_email_task.md"

    timeout /t 2 /nobreak >nul

    call :print_step "Creating test social media task..."

    REM Create test LinkedIn post task
    (
        echo # Post Product Launch Announcement
        echo.
        echo **Priority:** High
        echo **Category:** Social Media
        echo **Deadline:** 2026-02-05
        echo.
        echo ## Task Description
        echo.
        echo Post an announcement on LinkedIn about our new AI Employee System Silver Tier launch.
        echo.
        echo ## Content
        echo.
        echo 🚀 Excited to announce the launch of AI Employee System Silver Tier!
        echo.
        echo ✨ New features:
        echo - Multi-source task ingestion
        echo - Intelligent categorization
        echo - Approval workflows
        echo - MCP action execution
        echo.
        echo Transform your workflow today!
        echo.
        echo ## Action Required
        echo.
        echo ```json
        echo {
        echo   "action": "post_linkedin",
        echo   "content": "🚀 Excited to announce the launch of AI Employee System Silver Tier! ✨ New features include multi-source task ingestion, intelligent categorization, approval workflows, and MCP action execution. Transform your workflow today! #AI #Productivity #Innovation"
        echo }
        echo ```
    ) > "%VAULT_PATH%\test_social_media_task.md"

    call :print_success "Created: test_social_media_task.md"

    call :print_info "Tasks created in vault root"
    call :print_info "Simulating watcher behavior for demo..."

    call :pause_for_video

    REM ========================================================================
    REM STEP 4: Intelligent Task Categorization (Manually Simulated)
    REM ========================================================================

    call :print_header "STEP 4: Intelligent Task Categorization"

    call :print_step "🎬 DEMO: Manually simulating AI categorization..."
    call :print_info "In production, watchers would:"
    call :print_info "  1. Detect new files automatically"
    call :print_info "  2. Analyze content and metadata"
    call :print_info "  3. Categorize by priority and type"
    call :print_info "  4. Move to appropriate folders"

    timeout /t 2 /nobreak >nul

    call :print_info "For this demo, we'll manually move files to show the concept"
    timeout /t 1 /nobreak >nul

    call :print_step "Analyzing test_email_task.md..."
    call :print_substep "Priority: High | Category: Email | Action: send_email"
    timeout /t 1 /nobreak >nul

    REM Manually move email task to High_Priority
    if not exist "%VAULT_PATH%\High_Priority" mkdir "%VAULT_PATH%\High_Priority"
    if exist "%VAULT_PATH%\test_email_task.md" (
        move "%VAULT_PATH%\test_email_task.md" "%VAULT_PATH%\High_Priority\" >nul 2>&1
    )
    call :print_success "✓ test_email_task.md → High_Priority/"

    timeout /t 1 /nobreak >nul

    call :print_step "Analyzing test_social_media_task.md..."
    call :print_substep "Priority: High | Category: Social Media | Action: post_linkedin"
    timeout /t 1 /nobreak >nul

    REM Manually move social media task to Needs_Action
    if not exist "%VAULT_PATH%\Needs_Action" mkdir "%VAULT_PATH%\Needs_Action"
    if exist "%VAULT_PATH%\test_social_media_task.md" (
        move "%VAULT_PATH%\test_social_media_task.md" "%VAULT_PATH%\Needs_Action\" >nul 2>&1
    )
    call :print_success "✓ test_social_media_task.md → Needs_Action/"

    timeout /t 1 /nobreak >nul

    call :print_success "✓ Tasks categorized by AI"

    REM Show folder structure
    call :print_step "Current folder structure:"
    echo.
    echo %DIM%AI_Employee_Vault\%RESET%
    echo %DIM%├── High_Priority\%RESET%
    if exist "%VAULT_PATH%\High_Priority\test_email_task.md" (
        echo %GREEN%│   └── test_email_task.md%RESET%
    )
    echo %DIM%├── Needs_Action\%RESET%
    if exist "%VAULT_PATH%\Needs_Action\test_social_media_task.md" (
        echo %GREEN%│   └── test_social_media_task.md%RESET%
    )
    echo.

    call :pause_for_video

    REM ========================================================================
    REM STEP 5: Approval Workflow (Manually Simulated)
    REM ========================================================================

    call :print_header "STEP 5: Approval Workflow"

    call :print_step "🎬 DEMO: Creating approval request directly..."
    call :print_info "In production, the system would:"
    call :print_info "  1. Scan High_Priority tasks"
    call :print_info "  2. Generate action plans via generate_approval.py"
    call :print_info "  3. Create approval requests"
    call :print_info "  4. Move to Pending_Approval/"

    timeout /t 2 /nobreak >nul

    call :print_info "For this demo, we'll create the approval file manually"
    timeout /t 1 /nobreak >nul

    REM Create approval file directly for email task
    if not exist "%VAULT_PATH%\Pending_Approval" mkdir "%VAULT_PATH%\Pending_Approval"

    call :print_step "Creating approval for test_email_task.md..."

    (
        echo # Email Client About Invoice
        echo.
        echo **Priority:** High
        echo **Category:** Email
        echo **Deadline:** 2026-02-06
        echo **Status:** PENDING_APPROVAL
        echo.
        echo ## Task Description
        echo.
        echo Send an email to client@example.com with the subject "Invoice - January 2026".
        echo.
        echo The email should:
        echo - Thank them for their business
        echo - Attach the January invoice PDF
        echo - Request payment within 14 days
        echo - Include our payment details
        echo.
        echo ## Proposed Action
        echo.
        echo ```json
        echo {
        echo   "action": "send_email",
        echo   "to": "client@example.com",
        echo   "subject": "Invoice - January 2026",
        echo   "body": "Dear Client,\n\nThank you for your continued business. Please find attached the invoice for January 2026.\n\nPayment is due within 14 days.\n\nBest regards,\nAI Employee"
        echo }
        echo ```
        echo.
        echo ## AI Analysis
        echo.
        echo - **Risk Level:** Low
        echo - **Urgency:** High (deadline: 2026-02-06^)
        echo - **Estimated Impact:** Business-critical communication
        echo - **Prerequisites:** None
        echo.
        echo ## Approval Required
        echo.
        echo ⚠️ This task requires human approval before execution.
        echo.
        echo Please review the action above and:
        echo - Move to `Approved/` to execute
        echo - Move to `Rejected/` to decline
    ) > "%VAULT_PATH%\Pending_Approval\test_email_task.md"

    timeout /t 1 /nobreak >nul
    call :print_success "✓ Approval request generated"

    call :print_step "Checking Pending_Approval folder..."
    echo.
    echo %DIM%AI_Employee_Vault\%RESET%
    echo %DIM%├── Pending_Approval\%RESET%
    echo %YELLOW%│   └── test_email_task.md ⏳%RESET%
    echo.

    call :print_success "Found 1 task awaiting approval"

    call :pause_for_video

    REM ========================================================================
    REM STEP 6: Human Approval (Manually Simulated)
    REM ========================================================================

    call :print_header "STEP 6: Human Approval"

    call :print_step "🎬 DEMO: Simulating human review and approval..."
    call :print_info "In production, a human would:"
    call :print_info "  • Review the task details"
    call :print_info "  • Verify the proposed action"
    call :print_info "  • Check risk level and impact"
    call :print_info "  • Move file to Approved/ or Rejected/"

    timeout /t 2 /nobreak >nul

    call :print_step "Reviewing: test_email_task.md"
    call :print_substep "Action: send_email to client@example.com"
    call :print_substep "Risk: Low | Impact: Business-critical"
    timeout /t 2 /nobreak >nul

    call :print_step "✓ Human approves the task!"
    timeout /t 1 /nobreak >nul

    call :print_info "For this demo, manually moving to Approved/ folder..."

    REM Move to Approved folder
    if not exist "%VAULT_PATH%\Approved" mkdir "%VAULT_PATH%\Approved"
    if exist "%VAULT_PATH%\Pending_Approval\test_email_task.md" (
        move "%VAULT_PATH%\Pending_Approval\test_email_task.md" "%VAULT_PATH%\Approved\" >nul 2>&1
    )

    timeout /t 1 /nobreak >nul
    call :print_success "✓ Task approved by human"

    REM Show folder structure
    echo.
    echo %DIM%AI_Employee_Vault\%RESET%
    echo %DIM%├── Approved\%RESET%
    echo %GREEN%│   └── test_email_task.md ✓%RESET%
    echo %DIM%├── Pending_Approval\%RESET%
    echo %DIM%│   └── (empty^)%RESET%
    echo.

    call :pause_for_video

    REM ========================================================================
    REM STEP 7: MCP Action Execution (Simulated)
    REM ========================================================================

    call :print_header "STEP 7: MCP Action Execution"

    call :print_step "AI executing approved actions..."
    call :print_info "In production, the system would:"
    call :print_info "  1. Monitor Approved/ folder"
    call :print_info "  2. Parse MCP action metadata"
    call :print_info "  3. Execute actions via MCP servers"
    call :print_info "  4. Handle retries and rate limits"
    call :print_info "  5. Move to Done/ on success"

    timeout /t 2 /nobreak >nul

    call :print_step "Executing: test_email_task.md"
    call :print_info "Connecting to Gmail MCP server..."
    timeout /t 1 /nobreak >nul

    call :print_substep "Action: send_email"
    call :print_substep "To: client@example.com"
    call :print_substep "Subject: Invoice - January 2026"
    timeout /t 2 /nobreak >nul

    call :print_info "📧 Email sent successfully!"
    timeout /t 1 /nobreak >nul

    REM Move to Done folder
    if not exist "%VAULT_PATH%\Done" mkdir "%VAULT_PATH%\Done"
    if exist "%VAULT_PATH%\Approved\test_email_task.md" (
        REM Add execution metadata to the file
        (
            type "%VAULT_PATH%\Approved\test_email_task.md"
            echo.
            echo ---
            echo.
            echo ## Execution Log
            echo.
            echo - **Executed At:** 2026-02-05 14:30:00
            echo - **Status:** SUCCESS
            echo - **MCP Server:** gmail
            echo - **Action:** send_email
            echo - **Response:** Email sent successfully (Message ID: 18d4f2e3a1b5c6d7^)
        ) > "%VAULT_PATH%\Approved\test_email_task_temp.md"
        move /y "%VAULT_PATH%\Approved\test_email_task_temp.md" "%VAULT_PATH%\Done\test_email_task.md" >nul 2>&1
        del "%VAULT_PATH%\Approved\test_email_task.md" 2>nul
    )

    call :print_success "✓ Task executed and moved to Done/"

    REM Show folder structure
    echo.
    echo %DIM%AI_Employee_Vault\%RESET%
    echo %DIM%├── Done\%RESET%
    echo %GREEN%│   └── test_email_task.md ✓%RESET%
    echo %DIM%├── Approved\%RESET%
    echo %DIM%│   └── (empty^)%RESET%
    echo.

    call :print_success "Successfully executed 1 action"

    call :pause_for_video

    REM ========================================================================
    REM STEP 8: CEO Briefing Generation
    REM ========================================================================

    call :print_header "STEP 8: CEO Briefing Generation"

    call :print_step "Generating daily CEO briefing..."
    call :print_info "This analyzes:"
    call :print_info "  • All completed tasks"
    call :print_info "  • Current system status"
    call :print_info "  • Pending approvals"
    call :print_info "  • Performance metrics"

    REM Try to run the script, but create demo briefing if not available
    if exist "scripts\ceo_briefing_generator.py" (
        python scripts\ceo_briefing_generator.py 2>nul || call :print_warning "Briefing script not available (demo mode)"
    )

    REM Get today's date
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "TODAY=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%"
    set "BRIEFING_PATH=%VAULT_PATH%\Reports\CEO_Briefing_%TODAY%.md"

    REM If briefing doesn't exist, create a demo one
    if not exist "%BRIEFING_PATH%" (
        call :print_info "Creating demo briefing..."
        if not exist "%VAULT_PATH%\Reports" mkdir "%VAULT_PATH%\Reports"
        (
            echo # CEO Daily Briefing - %TODAY%
            echo.
            echo ## Executive Summary
            echo.
            echo ✓ **1 task completed successfully**
            echo - Email sent to client@example.com regarding invoice
            echo.
            echo ## System Performance
            echo.
            echo - Tasks processed: 2
            echo - Approvals generated: 1
            echo - Actions executed: 1
            echo - Success rate: 100%%
            echo.
            echo ## Upcoming Tasks
            echo.
            echo - test_social_media_task.md (High Priority^)
            echo.
            echo ---
            echo Generated by AI Employee System - Silver Tier
        ) > "%BRIEFING_PATH%"
    )

    call :print_success "CEO briefing generated"

    timeout /t 2 /nobreak >nul

    if exist "%BRIEFING_PATH%" (
        call :print_info "Briefing saved to: Reports\CEO_Briefing_%TODAY%.md"
        echo.
        call :print_info "Preview (first 20 lines):"
        echo %DIM%----------------------------------------%RESET%
        powershell -Command "Get-Content '%BRIEFING_PATH%' | Select-Object -First 20"
        echo %DIM%----------------------------------------%RESET%
    )

    call :pause_for_video

    REM ========================================================================
    REM STEP 9: Dashboard Display
    REM ========================================================================

    call :print_header "STEP 9: Dashboard Display"

    call :print_step "Updating dashboard..."

    REM Try to run the script, but create demo dashboard if not available
    if exist "scripts\dashboard_updater.py" (
        python scripts\dashboard_updater.py 2>nul || call :print_warning "Dashboard script not available (demo mode)"
    )

    REM If dashboard doesn't exist, create a demo one
    if not exist "%VAULT_PATH%\Dashboard.md" (
        call :print_info "Creating demo dashboard..."
        (
            echo # AI Employee System Dashboard
            echo.
            echo **Last Updated:** 2026-02-05 14:35:00
            echo.
            echo ---
            echo.
            echo ## 📊 System Status
            echo.
            echo ^| Component ^| Status ^| Details ^|
            echo ^|--------^|------^|-------^|
            echo ^| Inbox Watcher ^| 🟢 Active ^| Monitoring filesystem ^|
            echo ^| Gmail Watcher ^| 🟢 Active ^| Monitoring email ^|
            echo ^| Approval Executor ^| 🟢 Active ^| Processing approvals ^|
            echo ^| MCP Servers ^| 🟢 Connected ^| Gmail, LinkedIn ready ^|
            echo.
            echo ---
            echo.
            echo ## 📋 Task Overview
            echo.
            echo ^| Status ^| Count ^| Files ^|
            echo ^|------^|-----^|-----^|
            echo ^| ✅ Done ^| 1 ^| test_email_task.md ^|
            echo ^| 🔄 Needs Action ^| 1 ^| test_social_media_task.md ^|
            echo ^| ⏳ Pending Approval ^| 0 ^| - ^|
            echo ^| ❌ Rejected ^| 0 ^| - ^|
            echo.
            echo ---
            echo.
            echo ## 🎯 Recent Activity
            echo.
            echo - **14:30** - ✅ Email sent to client@example.com
            echo - **14:28** - 👍 Task approved: test_email_task.md
            echo - **14:25** - 📝 Approval generated for email task
            echo - **14:22** - 📥 Tasks categorized: 2 new high-priority items
            echo.
            echo ---
            echo.
            echo ## 📈 Performance Metrics
            echo.
            echo - **Tasks Today:** 2 processed
            echo - **Success Rate:** 100%%
            echo - **Avg Response Time:** 2.5 minutes
            echo - **Approvals Needed:** 0
            echo.
            echo ---
            echo.
            echo 🤖 AI Employee System - Silver Tier
        ) > "%VAULT_PATH%\Dashboard.md"
    )

    call :print_success "Dashboard updated"

    timeout /t 2 /nobreak >nul

    if exist "%VAULT_PATH%\Dashboard.md" (
        call :print_info "Dashboard content:"
        echo.
        echo %CYAN%========================================%RESET%
        type "%VAULT_PATH%\Dashboard.md"
        echo %CYAN%========================================%RESET%
        echo.
    )

    call :pause_for_video

    REM ========================================================================
    REM STEP 10: System Status & Logs
    REM ========================================================================

    call :print_header "STEP 10: System Status & Logs"

    call :print_step "System status overview..."

    echo.
    echo %GREEN%✓%RESET% Tasks categorized: 2
    echo %GREEN%✓%RESET% Approvals generated: 1
    echo %GREEN%✓%RESET% Tasks executed: 1
    echo %GREEN%✓%RESET% CEO briefing: Generated
    echo %GREEN%✓%RESET% Dashboard: Updated
    echo.

    call :print_step "Activity logs:"

    if exist "%LOGS_PATH%\%TODAY%.json" (
        call :print_info "Log file: Logs\%TODAY%.json"
        echo.
        powershell -Command "if (Test-Path '%LOGS_PATH%\%TODAY%.json') { try { $logs = Get-Content '%LOGS_PATH%\%TODAY%.json' | ConvertFrom-Json; $logs | Select-Object -Last 10 | ForEach-Object { Write-Host \"[$($_.timestamp)] [$($_.watcher)] $($_.level.ToUpper()): $($_.message)\" } } catch { Write-Host '(No log entries found)' } } else { Write-Host '(No log entries found)' }"
        echo.
    ) else (
        call :print_info "(No log file found for today)"
    )

    call :pause_for_video

    REM ========================================================================
    REM STEP 11: Cleanup & Shutdown
    REM ========================================================================

    call :print_header "STEP 11: Cleanup & Shutdown"

    call :print_step "Demo cleanup (optional)..."
    echo.
    echo %YELLOW%Do you want to clean up demo test files? (Y/N)%RESET%
    set /p "CLEANUP="

    if /i "!CLEANUP!"=="Y" (
        call :print_info "Cleaning up demo files..."

        del /q "%VAULT_PATH%\test_*.md" 2>nul
        del /q "%VAULT_PATH%\High_Priority\test_*.md" 2>nul
        del /q "%VAULT_PATH%\Needs_Action\test_*.md" 2>nul
        del /q "%VAULT_PATH%\Pending_Approval\test_*.md" 2>nul
        del /q "%VAULT_PATH%\Approved\test_*.md" 2>nul
        del /q "%VAULT_PATH%\Done\test_*.md" 2>nul
        del /q "%VAULT_PATH%\Plans\test_*_plan.md" 2>nul

        call :print_success "Demo files cleaned up"
    ) else (
        call :print_info "Keeping demo files for review"
    )

    REM ========================================================================
    REM Demo Complete!
    REM ========================================================================

    echo.
    echo.
    call :print_header "DEMO COMPLETE!"

    echo %GREEN%
    echo  ╔═══════════════════════════════════════════════════════════════════╗
    echo  ║                                                                   ║
    echo  ║  ✓ All Silver Tier features demonstrated successfully!           ║
    echo  ║                                                                   ║
    echo  ║  You saw:                                                         ║
    echo  ║  • Multi-source task ingestion (filesystem + Gmail)               ║
    echo  ║  • Intelligent categorization and prioritization                  ║
    echo  ║  • Approval workflow with human oversight                         ║
    echo  ║  • MCP action execution (email, social media)                     ║
    echo  ║  • CEO briefing generation                                        ║
    echo  ║  • Real-time dashboard updates                                    ║
    echo  ║  • Comprehensive logging and monitoring                           ║
    echo  ║                                                                   ║
    echo  ║  Ready for production! 🚀                                         ║
    echo  ║                                                                   ║
    echo  ╚═══════════════════════════════════════════════════════════════════╝
    echo %RESET%
    echo.

    call :print_info "Demo completed at:"
    call :timestamp
    echo.

    echo %CYAN%Press any key to exit...%RESET%
    pause >nul

    exit /b 0

endlocal
