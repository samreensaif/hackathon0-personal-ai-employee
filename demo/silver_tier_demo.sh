#!/bin/bash
# ============================================================================
# Silver Tier AI Employee System - Demo Script (Unix/Linux/Mac)
# ============================================================================
# This script demonstrates all Silver Tier features in an impressive sequence
# Perfect for recording demo videos!
#
# 🎬 DEMO MODE: This script simulates the workflow for demonstration purposes.
#    It manually moves files and creates outputs to showcase the CONCEPT
#    without requiring actual watchers, MCP servers, or API connections.
#
# Features demonstrated:
# 1. Watcher System (Inbox + Gmail) - Concept Overview
# 2. Intelligent Task Categorization - Simulated
# 3. Approval Workflow - Manual Simulation
# 4. MCP Action Execution - Visual Demonstration
# 5. CEO Briefing Generation - Created/Generated
# 6. Dashboard Updates - Created/Updated
#
# For production usage, use the actual watcher_manager.py and related scripts.
# ============================================================================

set -e  # Exit on error

# Colors using ANSI escape codes
readonly GREEN='\033[92m'
readonly YELLOW='\033[93m'
readonly BLUE='\033[94m'
readonly MAGENTA='\033[95m'
readonly CYAN='\033[96m'
readonly RED='\033[91m'
readonly BOLD='\033[1m'
readonly DIM='\033[2m'
readonly RESET='\033[0m'

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly VAULT_PATH="$PROJECT_ROOT/AI_Employee_Vault"
readonly DEMO_DATA="$PROJECT_ROOT/demo/test_data"
readonly LOGS_PATH="$VAULT_PATH/Logs"
readonly PAUSE_TIME=3

# Check for dry-run mode
DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
fi

# Detect Python command (cross-platform: Unix/Linux/Mac/Windows Git Bash)
# Check python first (Windows), then python3 (Unix/Linux/Mac)
if python --version &> /dev/null 2>&1; then
    PYTHON_CMD="python"
elif python3 --version &> /dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    echo "ERROR: Python not found! Please install Python 3.8+"
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# ============================================================================
# Helper Functions
# ============================================================================

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

print_header() {
    echo ""
    echo -e "${BOLD}${CYAN}============================================================================${RESET}"
    echo -e "${BOLD}${CYAN}$1${RESET}"
    echo -e "${BOLD}${CYAN}============================================================================${RESET}"
    echo ""
}

print_step() {
    echo -e "${GREEN}[$(timestamp)]${RESET} ${BOLD}$1${RESET}"
}

print_substep() {
    echo -e "${BLUE}  [$(timestamp)]${RESET} $1"
}

print_success() {
    echo -e "${GREEN}[$(timestamp)] ✓${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(timestamp)] ⚠${RESET} $1"
}

print_error() {
    echo -e "${RED}[$(timestamp)] ✗${RESET} $1"
}

print_info() {
    echo -e "${CYAN}[$(timestamp)] →${RESET} $1"
}

pause_for_video() {
    echo ""
    echo -e "${DIM}[PAUSE FOR VIDEO - Press any key to continue...]${RESET}"
    read -n 1 -s -r
}

# ============================================================================
# Main Demo Sequence
# ============================================================================

main() {
    clear

    # Banner
    echo -e "${BOLD}${MAGENTA}"
    cat << "EOF"
 ╔═══════════════════════════════════════════════════════════════════╗
 ║                                                                   ║
 ║        AI EMPLOYEE SYSTEM - SILVER TIER DEMO                      ║
 ║        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                        ║
 ║                                                                   ║
 ║        Showcasing:                                                ║
 ║        • Multi-source task ingestion                              ║
 ║        • Intelligent categorization                               ║
 ║        • Approval workflows                                       ║
 ║        • MCP action execution                                     ║
 ║        • CEO briefing generation                                  ║
 ║                                                                   ║
 ╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${RESET}"

    if [[ -n "$DRY_RUN" ]]; then
        print_warning "Running in DRY-RUN mode - no actual actions will be executed"
    fi

    echo ""
    echo -e "${YELLOW}Press any key to start the demo...${RESET}"
    read -n 1 -s -r
    echo ""

    # ========================================================================
    # STEP 1: Environment Setup & Cleanup
    # ========================================================================

    print_header "STEP 1: Environment Setup"

    print_step "Cleaning up previous demo data..."

    # Clean up old test files
    rm -f "$VAULT_PATH"/test_*.md 2>/dev/null || true
    print_substep "Removed old test files from vault root"

    rm -f "$VAULT_PATH"/High_Priority/test_*.md 2>/dev/null || true
    print_substep "Cleaned High_Priority folder"

    rm -f "$VAULT_PATH"/Needs_Action/test_*.md 2>/dev/null || true
    print_substep "Cleaned Needs_Action folder"

    rm -f "$VAULT_PATH"/Pending_Approval/test_*.md 2>/dev/null || true
    print_substep "Cleaned Pending_Approval folder"

    rm -f "$VAULT_PATH"/Approved/test_*.md 2>/dev/null || true
    print_substep "Cleaned Approved folder"

    rm -f "$VAULT_PATH"/Done/test_*.md 2>/dev/null || true
    print_substep "Cleaned Done folder"

    print_success "Environment cleaned and ready"

    print_step "Checking Python dependencies..."
    print_success "Python is available ($($PYTHON_CMD --version))"

    pause_for_video

    # ========================================================================
    # STEP 2: Watcher System (Concept Overview)
    # ========================================================================

    print_header "STEP 2: Watcher System Overview"

    print_step "Understanding the watcher architecture..."
    print_info "In production, the system includes:"
    print_info "  • Inbox Watcher (filesystem monitoring)"
    print_info "  • Gmail Watcher (email monitoring)"
    print_info "  • Continuous background processing"

    sleep 2

    print_info "For this demo, we'll simulate the workflow"
    print_success "✓ Watcher concept demonstrated"

    sleep 1

    pause_for_video

    # ========================================================================
    # STEP 3: Create Test Tasks
    # ========================================================================

    print_header "STEP 3: Creating Test Tasks"

    print_step "Creating test email task..."

    # Create test email task
    cat > "$VAULT_PATH/test_email_task.md" << 'EOF'
# Email Client About Invoice

**Priority:** High
**Category:** Email
**Deadline:** 2026-02-06

## Task Description

Send an email to client@example.com with the subject "Invoice - January 2026".

The email should:
- Thank them for their business
- Attach the January invoice PDF
- Request payment within 14 days
- Include our payment details

## Action Required

```json
{
  "action": "send_email",
  "to": "client@example.com",
  "subject": "Invoice - January 2026",
  "body": "Dear Client,\n\nThank you for your continued business. Please find attached the invoice for January 2026.\n\nPayment is due within 14 days.\n\nBest regards,\nAI Employee"
}
```
EOF

    print_success "Created: test_email_task.md"

    sleep 2

    print_step "Creating test social media task..."

    # Create test LinkedIn post task
    cat > "$VAULT_PATH/test_social_media_task.md" << 'EOF'
# Post Product Launch Announcement

**Priority:** High
**Category:** Social Media
**Deadline:** 2026-02-05

## Task Description

Post an announcement on LinkedIn about our new AI Employee System Silver Tier launch.

## Content

🚀 Excited to announce the launch of AI Employee System Silver Tier!

✨ New features:
- Multi-source task ingestion
- Intelligent categorization
- Approval workflows
- MCP action execution

Transform your workflow today!

## Action Required

```json
{
  "action": "post_linkedin",
  "content": "🚀 Excited to announce the launch of AI Employee System Silver Tier! ✨ New features include multi-source task ingestion, intelligent categorization, approval workflows, and MCP action execution. Transform your workflow today! #AI #Productivity #Innovation"
}
```
EOF

    print_success "Created: test_social_media_task.md"

    print_info "Tasks created in vault root"
    print_info "Simulating watcher behavior for demo..."

    pause_for_video

    # ========================================================================
    # STEP 4: Intelligent Task Categorization (Manually Simulated)
    # ========================================================================

    print_header "STEP 4: Intelligent Task Categorization"

    print_step "🎬 DEMO: Manually simulating AI categorization..."
    print_info "In production, watchers would:"
    print_info "  1. Detect new files automatically"
    print_info "  2. Analyze content and metadata"
    print_info "  3. Categorize by priority and type"
    print_info "  4. Move to appropriate folders"

    sleep 2

    print_info "For this demo, we'll manually move files to show the concept"
    sleep 1

    print_step "Analyzing test_email_task.md..."
    print_substep "Priority: High | Category: Email | Action: send_email"
    sleep 1

    # Manually move email task to High_Priority
    mkdir -p "$VAULT_PATH/High_Priority"
    mv "$VAULT_PATH/test_email_task.md" "$VAULT_PATH/High_Priority/" 2>/dev/null || true
    print_success "✓ test_email_task.md → High_Priority/"

    sleep 1

    print_step "Analyzing test_social_media_task.md..."
    print_substep "Priority: High | Category: Social Media | Action: post_linkedin"
    sleep 1

    # Manually move social media task to Needs_Action
    mkdir -p "$VAULT_PATH/Needs_Action"
    mv "$VAULT_PATH/test_social_media_task.md" "$VAULT_PATH/Needs_Action/" 2>/dev/null || true
    print_success "✓ test_social_media_task.md → Needs_Action/"

    sleep 1

    print_success "✓ Tasks categorized by AI"

    # Show folder structure
    print_step "Current folder structure:"
    echo ""
    echo -e "${DIM}AI_Employee_Vault/${RESET}"
    echo -e "${DIM}├── High_Priority/${RESET}"
    if [[ -f "$VAULT_PATH/High_Priority/test_email_task.md" ]]; then
        echo -e "${GREEN}│   └── test_email_task.md${RESET}"
    fi
    echo -e "${DIM}├── Needs_Action/${RESET}"
    if [[ -f "$VAULT_PATH/Needs_Action/test_social_media_task.md" ]]; then
        echo -e "${GREEN}│   └── test_social_media_task.md${RESET}"
    fi
    echo ""

    pause_for_video

    # ========================================================================
    # STEP 5: Approval Workflow (Manually Simulated)
    # ========================================================================

    print_header "STEP 5: Approval Workflow"

    print_step "🎬 DEMO: Creating approval request directly..."
    print_info "In production, the system would:"
    print_info "  1. Scan High_Priority tasks"
    print_info "  2. Generate action plans via generate_approval.py"
    print_info "  3. Create approval requests"
    print_info "  4. Move to Pending_Approval/"

    sleep 2

    print_info "For this demo, we'll create the approval file manually"
    sleep 1

    # Create approval file directly for email task
    mkdir -p "$VAULT_PATH/Pending_Approval"

    print_step "Creating approval for test_email_task.md..."

    cat > "$VAULT_PATH/Pending_Approval/test_email_task.md" << 'EOF'
# Email Client About Invoice

**Priority:** High
**Category:** Email
**Deadline:** 2026-02-06
**Status:** PENDING_APPROVAL

## Task Description

Send an email to client@example.com with the subject "Invoice - January 2026".

The email should:
- Thank them for their business
- Attach the January invoice PDF
- Request payment within 14 days
- Include our payment details

## Proposed Action

```json
{
  "action": "send_email",
  "to": "client@example.com",
  "subject": "Invoice - January 2026",
  "body": "Dear Client,\n\nThank you for your continued business. Please find attached the invoice for January 2026.\n\nPayment is due within 14 days.\n\nBest regards,\nAI Employee"
}
```

## AI Analysis

- **Risk Level:** Low
- **Urgency:** High (deadline: 2026-02-06)
- **Estimated Impact:** Business-critical communication
- **Prerequisites:** None

## Approval Required

⚠️ This task requires human approval before execution.

Please review the action above and:
- Move to `Approved/` to execute
- Move to `Rejected/` to decline
EOF

    sleep 1
    print_success "✓ Approval request generated"

    print_step "Checking Pending_Approval folder..."
    echo ""
    echo -e "${DIM}AI_Employee_Vault/${RESET}"
    echo -e "${DIM}├── Pending_Approval/${RESET}"
    echo -e "${YELLOW}│   └── test_email_task.md ⏳${RESET}"
    echo ""

    print_success "Found 1 task awaiting approval"

    pause_for_video

    # ========================================================================
    # STEP 6: Human Approval (Manually Simulated)
    # ========================================================================

    print_header "STEP 6: Human Approval"

    print_step "🎬 DEMO: Simulating human review and approval..."
    print_info "In production, a human would:"
    print_info "  • Review the task details"
    print_info "  • Verify the proposed action"
    print_info "  • Check risk level and impact"
    print_info "  • Move file to Approved/ or Rejected/"

    sleep 2

    print_step "Reviewing: test_email_task.md"
    print_substep "Action: send_email to client@example.com"
    print_substep "Risk: Low | Impact: Business-critical"
    sleep 2

    print_step "✓ Human approves the task!"
    sleep 1

    print_info "For this demo, manually moving to Approved/ folder..."

    # Move to Approved folder
    mkdir -p "$VAULT_PATH/Approved"
    mv "$VAULT_PATH/Pending_Approval/test_email_task.md" "$VAULT_PATH/Approved/" 2>/dev/null || true

    sleep 1
    print_success "✓ Task approved by human"

    # Show folder structure
    echo ""
    echo -e "${DIM}AI_Employee_Vault/${RESET}"
    echo -e "${DIM}├── Approved/${RESET}"
    echo -e "${GREEN}│   └── test_email_task.md ✓${RESET}"
    echo -e "${DIM}├── Pending_Approval/${RESET}"
    echo -e "${DIM}│   └── (empty)${RESET}"
    echo ""

    pause_for_video

    # ========================================================================
    # STEP 7: MCP Action Execution (Simulated)
    # ========================================================================

    print_header "STEP 7: MCP Action Execution"

    print_step "AI executing approved actions..."
    print_info "In production, the system would:"
    print_info "  1. Monitor Approved/ folder"
    print_info "  2. Parse MCP action metadata"
    print_info "  3. Execute actions via MCP servers"
    print_info "  4. Handle retries and rate limits"
    print_info "  5. Move to Done/ on success"

    sleep 2

    print_step "Executing: test_email_task.md"
    print_info "Connecting to Gmail MCP server..."
    sleep 1

    print_substep "Action: send_email"
    print_substep "To: client@example.com"
    print_substep "Subject: Invoice - January 2026"
    sleep 2

    print_info "📧 Email sent successfully!"
    sleep 1

    # Move to Done folder
    mkdir -p "$VAULT_PATH/Done"
    if [[ -f "$VAULT_PATH/Approved/test_email_task.md" ]]; then
        # Add execution metadata to the file
        cat >> "$VAULT_PATH/Approved/test_email_task.md" << 'EOF'

---

## Execution Log

- **Executed At:** 2026-02-05 14:30:00
- **Status:** SUCCESS
- **MCP Server:** gmail
- **Action:** send_email
- **Response:** Email sent successfully (Message ID: 18d4f2e3a1b5c6d7)
EOF
        mv "$VAULT_PATH/Approved/test_email_task.md" "$VAULT_PATH/Done/" 2>/dev/null || true
    fi

    print_success "✓ Task executed and moved to Done/"

    # Show folder structure
    echo ""
    echo -e "${DIM}AI_Employee_Vault/${RESET}"
    echo -e "${DIM}├── Done/${RESET}"
    echo -e "${GREEN}│   └── test_email_task.md ✓${RESET}"
    echo -e "${DIM}├── Approved/${RESET}"
    echo -e "${DIM}│   └── (empty)${RESET}"
    echo ""

    print_success "Successfully executed 1 action"

    pause_for_video

    # ========================================================================
    # STEP 8: CEO Briefing Generation
    # ========================================================================

    print_header "STEP 8: CEO Briefing Generation"

    print_step "Generating daily CEO briefing..."
    print_info "This analyzes:"
    print_info "  • All completed tasks"
    print_info "  • Current system status"
    print_info "  • Pending approvals"
    print_info "  • Performance metrics"

    # Try to run the script, but don't fail if it doesn't work
    if [[ -f "scripts/ceo_briefing_generator.py" ]]; then
        $PYTHON_CMD scripts/ceo_briefing_generator.py 2>/dev/null || print_warning "Briefing script not available (demo mode)"
    else
        print_info "Creating demo briefing..."
        mkdir -p "$VAULT_PATH/Reports"
        TODAY=$(date +%Y-%m-%d)
        cat > "$VAULT_PATH/Reports/CEO_Briefing_$TODAY.md" << EOF
# CEO Daily Briefing - $TODAY

## Executive Summary

✓ **1 task completed successfully**
- Email sent to client@example.com regarding invoice

## System Performance

- Tasks processed: 2
- Approvals generated: 1
- Actions executed: 1
- Success rate: 100%

## Upcoming Tasks

- test_social_media_task.md (High Priority)

---
Generated by AI Employee System - Silver Tier
EOF
    fi

    print_success "CEO briefing generated"

    sleep 2

    # Show briefing path
    TODAY=$(date +%Y-%m-%d)
    BRIEFING_PATH="$VAULT_PATH/Reports/CEO_Briefing_$TODAY.md"

    if [[ -f "$BRIEFING_PATH" ]]; then
        print_info "Briefing saved to: Reports/CEO_Briefing_$TODAY.md"
        echo ""
        print_info "Preview (first 20 lines):"
        echo -e "${DIM}----------------------------------------${RESET}"
        head -n 20 "$BRIEFING_PATH"
        echo -e "${DIM}----------------------------------------${RESET}"
    fi

    pause_for_video

    # ========================================================================
    # STEP 9: Dashboard Display
    # ========================================================================

    print_header "STEP 9: Dashboard Display"

    print_step "Updating dashboard..."

    # Try to run the script, but create demo dashboard if not available
    if [[ -f "scripts/dashboard_updater.py" ]]; then
        $PYTHON_CMD scripts/dashboard_updater.py 2>/dev/null || print_warning "Dashboard script not available (demo mode)"
    fi

    # If dashboard doesn't exist, create a demo one
    if [[ ! -f "$VAULT_PATH/Dashboard.md" ]]; then
        print_info "Creating demo dashboard..."
        cat > "$VAULT_PATH/Dashboard.md" << 'EOF'
# AI Employee System Dashboard

**Last Updated:** 2026-02-05 14:35:00

---

## 📊 System Status

| Component | Status | Details |
|-----------|--------|---------|
| Inbox Watcher | 🟢 Active | Monitoring filesystem |
| Gmail Watcher | 🟢 Active | Monitoring email |
| Approval Executor | 🟢 Active | Processing approvals |
| MCP Servers | 🟢 Connected | Gmail, LinkedIn ready |

---

## 📋 Task Overview

| Status | Count | Files |
|--------|-------|-------|
| ✅ Done | 1 | test_email_task.md |
| 🔄 Needs Action | 1 | test_social_media_task.md |
| ⏳ Pending Approval | 0 | - |
| ❌ Rejected | 0 | - |

---

## 🎯 Recent Activity

- **14:30** - ✅ Email sent to client@example.com
- **14:28** - 👍 Task approved: test_email_task.md
- **14:25** - 📝 Approval generated for email task
- **14:22** - 📥 Tasks categorized: 2 new high-priority items

---

## 📈 Performance Metrics

- **Tasks Today:** 2 processed
- **Success Rate:** 100%
- **Avg Response Time:** 2.5 minutes
- **Approvals Needed:** 0

---

🤖 AI Employee System - Silver Tier
EOF
    fi

    print_success "Dashboard updated"

    sleep 2

    if [[ -f "$VAULT_PATH/Dashboard.md" ]]; then
        print_info "Dashboard content:"
        echo ""
        echo -e "${CYAN}========================================${RESET}"
        cat "$VAULT_PATH/Dashboard.md"
        echo -e "${CYAN}========================================${RESET}"
        echo ""
    fi

    pause_for_video

    # ========================================================================
    # STEP 10: System Status & Logs
    # ========================================================================

    print_header "STEP 10: System Status & Logs"

    print_step "System status overview..."

    echo ""
    echo -e "${GREEN}✓${RESET} Tasks categorized: 2"
    echo -e "${GREEN}✓${RESET} Approvals generated: 1"
    echo -e "${GREEN}✓${RESET} Tasks executed: 1"
    echo -e "${GREEN}✓${RESET} CEO briefing: Generated"
    echo -e "${GREEN}✓${RESET} Dashboard: Updated"
    echo ""

    print_step "Activity logs:"

    if [[ -f "$LOGS_PATH/$TODAY.json" ]]; then
        print_info "Log file: Logs/$TODAY.json"
        echo ""
        $PYTHON_CMD << EOF
import json
try:
    with open('$LOGS_PATH/$TODAY.json', 'r') as f:
        logs = json.load(f)
        for log in logs[-10:]:
            print(f"[{log['timestamp']}] [{log.get('watcher', 'system')}] {log['level'].upper()}: {log['message']}")
except:
    print("(No log entries found)")
EOF
        echo ""
    else
        print_info "(No log file found for today)"
    fi

    pause_for_video

    # ========================================================================
    # STEP 11: Cleanup & Shutdown
    # ========================================================================

    print_header "STEP 11: Cleanup & Shutdown"

    print_step "Demo cleanup (optional)..."
    echo ""
    echo -e "${YELLOW}Do you want to clean up demo test files? (y/n)${RESET}"
    read -n 1 -r CLEANUP
    echo ""

    if [[ $CLEANUP =~ ^[Yy]$ ]]; then
        print_info "Cleaning up demo files..."

        rm -f "$VAULT_PATH"/test_*.md 2>/dev/null || true
        rm -f "$VAULT_PATH"/High_Priority/test_*.md 2>/dev/null || true
        rm -f "$VAULT_PATH"/Needs_Action/test_*.md 2>/dev/null || true
        rm -f "$VAULT_PATH"/Pending_Approval/test_*.md 2>/dev/null || true
        rm -f "$VAULT_PATH"/Approved/test_*.md 2>/dev/null || true
        rm -f "$VAULT_PATH"/Done/test_*.md 2>/dev/null || true
        rm -f "$VAULT_PATH"/Plans/test_*_plan.md 2>/dev/null || true

        print_success "Demo files cleaned up"
    else
        print_info "Keeping demo files for review"
    fi

    # ========================================================================
    # Demo Complete!
    # ========================================================================

    echo ""
    echo ""
    print_header "DEMO COMPLETE!"

    echo -e "${GREEN}"
    cat << "EOF"
 ╔═══════════════════════════════════════════════════════════════════╗
 ║                                                                   ║
 ║  ✓ All Silver Tier features demonstrated successfully!           ║
 ║                                                                   ║
 ║  You saw:                                                         ║
 ║  • Multi-source task ingestion (filesystem + Gmail)               ║
 ║  • Intelligent categorization and prioritization                  ║
 ║  • Approval workflow with human oversight                         ║
 ║  • MCP action execution (email, social media)                     ║
 ║  • CEO briefing generation                                        ║
 ║  • Real-time dashboard updates                                    ║
 ║  • Comprehensive logging and monitoring                           ║
 ║                                                                   ║
 ║  Ready for production! 🚀                                         ║
 ║                                                                   ║
 ╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${RESET}"
    echo ""

    print_info "Demo completed at: $(timestamp)"
    echo ""

    echo -e "${CYAN}Press any key to exit...${RESET}"
    read -n 1 -s -r

    exit 0
}

# ============================================================================
# Entry Point
# ============================================================================

# Trap Ctrl+C to cleanup
trap 'echo ""; print_warning "Demo interrupted"; exit 130' INT

main "$@"
