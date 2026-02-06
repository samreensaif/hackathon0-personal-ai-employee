---
name: Dashboard Updater
slug: dashboard-updater
description: Maintains real-time Dashboard.md with task metrics, system status, and activity feed
version: 1.0.0
author: AI Employee System
tier: silver
status: active
created: 2026-02-05
last_updated: 2026-02-05
dependencies:
  - task_processor
  - email_handler
---

# Dashboard Updater Skill

## 📋 Purpose

Maintain a real-time Dashboard.md file that provides at-a-glance visibility into the AI Employee system's status, task metrics, recent activity, approval queue, and performance statistics. Automatically updates after every task processor run and system action.

---

## ⚡ Triggers

### Automatic Triggers
- **Post-Task Processing:** After `runner_silver.py` completes
- **Post-Email Action:** After `email_handler.py` executes
- **Post-Approval:** After `approval_executor.py` runs
- **Scheduled:** Every 5 minutes (optional background refresh)
- **File Event:** New file added to any vault folder

### Manual Triggers
- **Command:** "Update the dashboard"
- **Command:** "Show system status"
- **Command:** "What's the current task status?"
- **Script:** `python scripts/dashboard_updater.py`

---

## 📥 Inputs

### Input Sources

#### 1. Vault Folder Structure
```
AI_Employee_Vault/
├── Needs_Action/       → Count pending tasks
├── High_Priority/      → Count urgent tasks
├── Pending_Approval/   → Count awaiting approval
├── Approved/           → Count approved actions
├── Done/               → Count completed tasks
├── Failed/             → Count failed attempts
├── Plans/              → Count execution plans
└── Logs/               → Parse activity history
```

#### 2. Log Files
```yaml
# From: Logs/YYYY-MM-DD.json
- Recent actions (last 10-20 entries)
- Task processing events
- Email actions
- Approval events
- Error logs
```

#### 3. Rate Limit Data
```yaml
# From: Logs/rate_limits.json
- Email send count
- Draft count
- Search count
- Remaining capacity
```

#### 4. Approval Files
```yaml
# From: Pending_Approval/*.md
- Parse metadata
- Extract action type
- Get creation timestamp
- Calculate wait time
```

---

## 📤 Outputs

### Main Output: Dashboard.md

**Location:** `AI_Employee_Vault/Dashboard.md`

**Structure:**
```markdown
# AI Employee Dashboard

🤖 **Last Updated:** 2026-02-05 17:30:00

---

## 📊 Task Overview

| Folder | Count | Status |
|--------|-------|--------|
| 🔴 High Priority | 2 | ⚠️ Action Required |
| 🟡 Pending Approval | 3 | 👤 Human Review Needed |
| 🔵 Needs Action | 5 | 📋 Queued |
| ✅ Done (Today) | 12 | ✓ Completed |
| ❌ Failed | 0 | ✓ OK |

**Total Active Tasks:** 10
**Completion Rate Today:** 70.6% (12/17)

---

## 🎯 System Status

🟢 **OPERATIONAL** - All systems functioning normally

| Component | Status | Last Check |
|-----------|--------|------------|
| Task Processor | 🟢 Online | 2 min ago |
| Email Handler | 🟢 Online | 5 min ago |
| Approval Executor | 🟢 Ready | 1 min ago |
| MCP Servers | 🟢 Connected | 30 sec ago |

---

## 📋 Approval Queue

**Items Awaiting Approval:** 3

1. **Send Invoice Email** - client@example.com
   - Created: 15 minutes ago
   - Priority: Medium
   - Action: `Pending_Approval/send_invoice_approval.md`

2. **Send Partnership Proposal** - partner@startup.com
   - Created: 1 hour ago
   - Priority: High
   - Action: `Pending_Approval/send_partnership_approval.md`

3. **Send Contract Update** - vendor@example.com
   - Created: 3 hours ago
   - Priority: Medium
   - Action: `Pending_Approval/send_contract_approval.md`

⚠️ **1 approval overdue** (>2 hours old)

---

## 📈 Today's Statistics

**Date:** February 5, 2026

### Task Processing
- **Total Processed:** 17 tasks
- **Auto-Completed:** 3 tasks (17.6%)
- **Routed to High Priority:** 2 tasks (11.8%)
- **Sent for Approval:** 3 tasks (17.6%)
- **Completed:** 12 tasks (70.6%)
- **Failed:** 0 tasks (0%)

### Email Activity
- **Drafts Created:** 5
- **Emails Sent:** 2
- **Searches Performed:** 8
- **Emails Categorized:** 47

### Rate Limits
- **Email Sends:** 2/10 (20% capacity)
- **Email Drafts:** 5/50 (10% capacity)
- **Email Searches:** 8/100 (8% capacity)

### Performance
- **Avg Processing Time:** 2.3 seconds/task
- **Success Rate:** 100%
- **Uptime:** 23 hours 45 minutes

---

## 🔔 Recent Activity

**Last 10 Actions:**

1. **17:28** - Task Processed: `research_competitors.md` → High Priority ⚠️
2. **17:25** - Email Sent: client@example.com - Invoice January 2026 ✓
3. **17:20** - Draft Created: partner@startup.com - Partnership Proposal ✓
4. **17:15** - Task Processed: `team_meeting_notes.md` → Done (Auto) ✓
5. **17:10** - Approval Created: Send email to client@example.com 👤
6. **17:05** - Search: from:vendor@example.com subject:invoice (5 results) 🔍
7. **17:00** - Task Processed: `weekly_report.md` → Done ✓
8. **16:55** - Email Categorized: 23 emails (3 urgent, 8 response) 📊
9. **16:50** - Draft Created: team@company.com - Meeting Summary ✓
10. **16:45** - Task Processed: `urgent_bug_fix.md` → High Priority ⚠️

---

## 🚀 Quick Actions

### For You
- [ ] **Review 3 pending approvals** in `Pending_Approval/`
- [ ] **Address 2 high priority tasks** in `High_Priority/`
- [ ] **Process 5 pending tasks** in `Needs_Action/`

### Next Steps
1. Run approval executor: `python scripts/approval_executor.py`
2. Review high priority: `urgent_bug_fix.md`, `research_competitors.md`
3. Check overdue approval: `send_contract_approval.md` (3 hours old)

---

## 📊 Weekly Summary

**This Week** (Feb 3-5, 2026)

- Total Tasks: 52
- Completed: 45 (86.5%)
- Pending: 7 (13.5%)
- Avg Daily: 17.3 tasks
- Top Category: Email Operations (45%)

**Trending:** ⬆️ +23% increase in email activity vs last week

---

**Dashboard Auto-Updates:** Every 5 minutes
**Manual Refresh:** Run `python scripts/dashboard_updater.py`
```

---

## 🎯 Capabilities

### 1. Count Tasks in Each Folder

**Purpose:** Provide real-time task distribution across all vault folders.

**Implementation:**
```python
def count_tasks_by_folder() -> Dict[str, int]:
    """
    Count .md files in each vault folder.

    Returns:
        {
            'needs_action': 5,
            'high_priority': 2,
            'pending_approval': 3,
            'approved': 8,
            'done': 12,
            'failed': 0
        }
    """
    pass
```

**Display:**
```markdown
| Folder | Count | Status |
|--------|-------|--------|
| 🔴 High Priority | 2 | ⚠️ Action Required |
| 🟡 Pending Approval | 3 | 👤 Human Review Needed |
| 🔵 Needs Action | 5 | 📋 Queued |
```

---

### 2. Show Recent Activity (Last 10 Actions)

**Purpose:** Display chronological feed of recent system actions for transparency.

**Implementation:**
```python
def get_recent_activity(limit: int = 10) -> List[Dict]:
    """
    Read daily log files and extract recent actions.

    Returns:
        [
            {
                'timestamp': '17:28',
                'action': 'task_processed',
                'description': 'research_competitors.md → High Priority',
                'icon': '⚠️'
            },
            ...
        ]
    """
    pass
```

**Display:**
```markdown
## 🔔 Recent Activity

1. **17:28** - Task Processed: `research_competitors.md` → High Priority ⚠️
2. **17:25** - Email Sent: client@example.com - Invoice January ✓
3. **17:20** - Draft Created: partner@startup.com - Proposal ✓
```

---

### 3. Display System Status

**Purpose:** Show health status of all system components and MCP servers.

**Implementation:**
```python
def check_system_status() -> Dict[str, str]:
    """
    Check status of all components.

    Returns:
        {
            'overall': 'operational',  # operational, degraded, down
            'task_processor': 'online',
            'email_handler': 'online',
            'approval_executor': 'ready',
            'mcp_gmail': 'connected',
            'last_check': '2026-02-05T17:30:00'
        }
    """
    pass
```

**Status Indicators:**
- 🟢 **Online/Connected** - Fully operational
- 🟡 **Degraded** - Operating with issues
- 🔴 **Down/Offline** - Not functioning
- ⚪ **Unknown** - Status cannot be determined

**Display:**
```markdown
## 🎯 System Status

🟢 **OPERATIONAL** - All systems functioning normally

| Component | Status | Last Check |
|-----------|--------|------------|
| Task Processor | 🟢 Online | 2 min ago |
| Email Handler | 🟢 Online | 5 min ago |
```

---

### 4. Show Approval Queue

**Purpose:** List all pending approvals with age and priority for human review.

**Implementation:**
```python
def get_approval_queue() -> List[Dict]:
    """
    Parse all files in Pending_Approval/ folder.

    Returns:
        [
            {
                'action': 'Send Invoice Email',
                'recipient': 'client@example.com',
                'created': '2026-02-05T17:00:00',
                'age_minutes': 30,
                'priority': 'medium',
                'file': 'send_invoice_approval.md',
                'overdue': False
            },
            ...
        ]
    """
    pass
```

**Display:**
```markdown
## 📋 Approval Queue

**Items Awaiting Approval:** 3

1. **Send Invoice Email** - client@example.com
   - Created: 15 minutes ago
   - Priority: Medium
   - Action: `Pending_Approval/send_invoice_approval.md`

⚠️ **1 approval overdue** (>2 hours old)
```

**Overdue Threshold:** 2 hours (configurable)

---

### 5. Calculate Task Completion Rate

**Purpose:** Provide metrics on task throughput and success rate.

**Implementation:**
```python
def calculate_completion_rate(date: str = "today") -> Dict:
    """
    Calculate task completion metrics.

    Args:
        date: 'today', 'yesterday', 'this_week', or 'YYYY-MM-DD'

    Returns:
        {
            'total_processed': 17,
            'completed': 12,
            'in_progress': 5,
            'failed': 0,
            'completion_rate': 70.6,
            'auto_completion_rate': 17.6,
            'approval_rate': 17.6,
            'avg_processing_time': 2.3
        }
    """
    pass
```

**Formulas:**
- **Completion Rate** = (Completed / Total Processed) × 100%
- **Auto-Completion Rate** = (Auto-Completed / Total Processed) × 100%
- **Approval Rate** = (Sent for Approval / Total Processed) × 100%
- **Success Rate** = ((Total - Failed) / Total) × 100%

**Display:**
```markdown
**Completion Rate Today:** 70.6% (12/17)

### Task Processing
- **Total Processed:** 17 tasks
- **Completed:** 12 tasks (70.6%)
- **Auto-Completed:** 3 tasks (17.6%)
- **Failed:** 0 tasks (0%)
```

---

### 6. Show Today's Statistics

**Purpose:** Comprehensive daily metrics for all system activities.

**Implementation:**
```python
def get_daily_statistics() -> Dict:
    """
    Aggregate all statistics for today.

    Returns:
        {
            'date': '2026-02-05',
            'tasks': {
                'total': 17,
                'completed': 12,
                'auto_completed': 3,
                'high_priority': 2,
                'approval_required': 3,
                'failed': 0
            },
            'emails': {
                'drafts': 5,
                'sent': 2,
                'searches': 8,
                'categorized': 47
            },
            'rate_limits': {
                'send_email': {'used': 2, 'limit': 10},
                'draft_email': {'used': 5, 'limit': 50},
                'search_emails': {'used': 8, 'limit': 100}
            },
            'performance': {
                'avg_processing_time': 2.3,
                'success_rate': 100.0,
                'uptime_hours': 23.75
            }
        }
    """
    pass
```

**Display:**
```markdown
## 📈 Today's Statistics

**Date:** February 5, 2026

### Task Processing
- **Total Processed:** 17 tasks
- **Completed:** 12 tasks (70.6%)
- **Success Rate:** 100%

### Email Activity
- **Drafts Created:** 5
- **Emails Sent:** 2/10 (20% capacity)

### Performance
- **Avg Processing Time:** 2.3 seconds/task
- **Uptime:** 23 hours 45 minutes
```

---

## 🔄 Process Flow

### Main Update Flow

```
Trigger Event (task processed, email sent, etc.)
    ↓
Load current dashboard state (if exists)
    ↓
Gather Data:
  - Count tasks in all folders
  - Read today's log file
  - Check rate limits
  - Parse approval queue
  - Calculate metrics
    ↓
Generate Dashboard Sections:
  - Task Overview (counts + status)
  - System Status (component health)
  - Approval Queue (sorted by age)
  - Today's Statistics (aggregated metrics)
  - Recent Activity (last 10 actions)
  - Quick Actions (action items for user)
    ↓
Render Dashboard.md:
  - Use templates for each section
  - Format with markdown tables
  - Add status icons
  - Include timestamps
    ↓
Write to AI_Employee_Vault/Dashboard.md
    ↓
Log dashboard update action
    ↓
Return update summary
```

---

### Detailed Step-by-Step

#### Step 1: Count Tasks
```python
counts = {
    'needs_action': len(list(NEEDS_ACTION_PATH.glob("*.md"))),
    'high_priority': len(list(HIGH_PRIORITY_PATH.glob("*.md"))),
    'pending_approval': len(list(PENDING_APPROVAL_PATH.glob("*.md"))),
    'done': len(list(DONE_PATH.glob("*.md"))),
    'failed': len(list(FAILED_PATH.glob("*.md")))
}
```

#### Step 2: Read Recent Activity
```python
# Load today's log
with open(LOGS_PATH / f"{today}.json") as f:
    logs = json.load(f)

# Get last 10 actions
recent = logs[-10:]

# Format for display
activity = []
for log in reversed(recent):
    activity.append({
        'time': log['timestamp'][-8:-3],  # HH:MM
        'description': format_log_entry(log),
        'icon': get_icon_for_action(log['action'])
    })
```

#### Step 3: Check System Status
```python
# Check each component
status = {
    'task_processor': check_last_run('task_processor'),
    'email_handler': check_last_run('email_handler'),
    'approval_executor': check_last_run('approval_executor'),
    'mcp_gmail': check_mcp_connection('gmail')
}

# Determine overall status
if all(s == 'online' for s in status.values()):
    overall = 'operational'
elif any(s == 'down' for s in status.values()):
    overall = 'degraded'
else:
    overall = 'operational'
```

#### Step 4: Parse Approval Queue
```python
approvals = []
for approval_file in PENDING_APPROVAL_PATH.glob("*.md"):
    metadata = parse_yaml_frontmatter(approval_file)

    if metadata.get('approval_status') == 'pending':
        age = datetime.now() - parse_datetime(metadata['created_at'])

        approvals.append({
            'action': extract_action_title(approval_file),
            'recipient': metadata.get('mcp_params', {}).get('to'),
            'age_minutes': age.total_seconds() / 60,
            'priority': metadata.get('priority', 'medium'),
            'file': approval_file.name,
            'overdue': age.total_seconds() > 7200  # 2 hours
        })

# Sort by age (oldest first)
approvals.sort(key=lambda x: x['age_minutes'], reverse=True)
```

#### Step 5: Calculate Metrics
```python
# Load today's logs
logs = load_daily_logs(today)

# Count by action type
task_logs = [l for l in logs if 'task' in l.get('action', '')]
completed = len([l for l in task_logs if l.get('success')])
failed = len([l for l in task_logs if not l.get('success')])

# Calculate rates
total = len(task_logs)
completion_rate = (completed / total * 100) if total > 0 else 0
```

#### Step 6: Render Dashboard
```python
dashboard_content = f"""# AI Employee Dashboard

🤖 **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{render_task_overview(counts)}

---

{render_system_status(status)}

---

{render_approval_queue(approvals)}

---

{render_daily_statistics(statistics)}

---

{render_recent_activity(activity)}

---

{render_quick_actions(counts, approvals)}
"""

# Write to file
with open(VAULT_PATH / "Dashboard.md", "w") as f:
    f.write(dashboard_content)
```

---

## 📝 Dashboard Templates

### Template 1: Task Overview

```markdown
## 📊 Task Overview

| Folder | Count | Status |
|--------|-------|--------|
| 🔴 High Priority | {high_priority_count} | {high_priority_status} |
| 🟡 Pending Approval | {pending_approval_count} | {pending_approval_status} |
| 🔵 Needs Action | {needs_action_count} | {needs_action_status} |
| ✅ Done (Today) | {done_today_count} | ✓ Completed |
| ❌ Failed | {failed_count} | {failed_status} |

**Total Active Tasks:** {active_total}
**Completion Rate Today:** {completion_rate}% ({completed}/{total})
```

**Status Logic:**
- High Priority > 0: "⚠️ Action Required"
- High Priority = 0: "✓ Clear"
- Pending Approval > 3: "⚠️ Review Backlog"
- Pending Approval 1-3: "👤 Human Review Needed"
- Pending Approval = 0: "✓ Clear"
- Failed > 0: "❌ Errors Present"
- Failed = 0: "✓ OK"

---

### Template 2: System Status

```markdown
## 🎯 System Status

{overall_status_icon} **{OVERALL_STATUS}** - {status_description}

| Component | Status | Last Check |
|-----------|--------|------------|
| Task Processor | {task_processor_icon} {task_processor_status} | {task_processor_age} |
| Email Handler | {email_handler_icon} {email_handler_status} | {email_handler_age} |
| Approval Executor | {approval_executor_icon} {approval_executor_status} | {approval_executor_age} |
| MCP Servers | {mcp_icon} {mcp_status} | {mcp_age} |
```

**Icon Mapping:**
- online/connected: 🟢
- degraded/warning: 🟡
- down/offline: 🔴
- unknown: ⚪

---

### Template 3: Approval Queue

```markdown
## 📋 Approval Queue

**Items Awaiting Approval:** {approval_count}

{#if approval_count > 0}
{#for approval in approvals}
{index}. **{approval.action}** - {approval.recipient}
   - Created: {approval.age_human}
   - Priority: {approval.priority}
   - Action: `{approval.file}`
{#endfor}

{#if overdue_count > 0}
⚠️ **{overdue_count} approval(s) overdue** (>2 hours old)
{#endif}

{#else}
✅ **No pending approvals** - All caught up!
{#endif}
```

---

### Template 4: Today's Statistics

```markdown
## 📈 Today's Statistics

**Date:** {date_formatted}

### Task Processing
- **Total Processed:** {tasks.total} tasks
- **Auto-Completed:** {tasks.auto_completed} tasks ({tasks.auto_completed_pct}%)
- **Routed to High Priority:** {tasks.high_priority} tasks ({tasks.high_priority_pct}%)
- **Sent for Approval:** {tasks.approval_required} tasks ({tasks.approval_required_pct}%)
- **Completed:** {tasks.completed} tasks ({tasks.completed_pct}%)
- **Failed:** {tasks.failed} tasks ({tasks.failed_pct}%)

### Email Activity
- **Drafts Created:** {emails.drafts}
- **Emails Sent:** {emails.sent}
- **Searches Performed:** {emails.searches}
- **Emails Categorized:** {emails.categorized}

### Rate Limits
- **Email Sends:** {rate_limits.send_email.used}/{rate_limits.send_email.limit} ({rate_limits.send_email.pct}% capacity)
- **Email Drafts:** {rate_limits.draft_email.used}/{rate_limits.draft_email.limit} ({rate_limits.draft_email.pct}% capacity)
- **Email Searches:** {rate_limits.search_emails.used}/{rate_limits.search_emails.limit} ({rate_limits.search_emails.pct}% capacity)

### Performance
- **Avg Processing Time:** {performance.avg_time} seconds/task
- **Success Rate:** {performance.success_rate}%
- **Uptime:** {performance.uptime_human}
```

---

### Template 5: Recent Activity

```markdown
## 🔔 Recent Activity

**Last {activity_count} Actions:**

{#for activity in recent_activity}
{index}. **{activity.time}** - {activity.description} {activity.icon}
{#endfor}
```

**Action Formatting:**
- Task processed: `Task Processed: filename.md → Destination`
- Email sent: `Email Sent: recipient - subject`
- Draft created: `Draft Created: recipient - subject`
- Approval created: `Approval Created: action description`
- Search performed: `Search: query (N results)`
- Categorization: `Email Categorized: N emails (X urgent, Y response)`

---

### Template 6: Quick Actions

```markdown
## 🚀 Quick Actions

### For You
{#if pending_approval_count > 0}
- [ ] **Review {pending_approval_count} pending approval(s)** in `Pending_Approval/`
{#endif}
{#if high_priority_count > 0}
- [ ] **Address {high_priority_count} high priority task(s)** in `High_Priority/`
{#endif}
{#if needs_action_count > 0}
- [ ] **Process {needs_action_count} pending task(s)** in `Needs_Action/`
{#endif}

### Next Steps
{#if has_approvals}
1. Run approval executor: `python scripts/approval_executor.py`
{#endif}
{#if has_high_priority}
2. Review high priority: {high_priority_files}
{#endif}
{#if has_overdue_approvals}
3. Check overdue approval(s): {overdue_files}
{#endif}
```

---

### Template 7: Weekly Summary (Optional)

```markdown
## 📊 Weekly Summary

**This Week** ({week_start} - {week_end})

- Total Tasks: {week.total}
- Completed: {week.completed} ({week.completed_pct}%)
- Pending: {week.pending} ({week.pending_pct}%)
- Avg Daily: {week.avg_daily} tasks
- Top Category: {week.top_category} ({week.top_category_pct}%)

**Trending:** {week.trend_icon} {week.trend_text}
```

---

## 💻 Code Reference

### Main Implementation

**File:** `scripts/dashboard_updater.py`

**Key Functions:**

```python
def update_dashboard(trigger_event: str = None) -> Dict:
    """
    Main function to update the dashboard.

    Args:
        trigger_event: Optional event that triggered update

    Returns:
        {
            'success': bool,
            'updated_at': str,
            'sections_updated': list,
            'metrics': dict
        }
    """
    pass


def count_tasks_by_folder() -> Dict[str, int]:
    """Count .md files in each vault folder."""
    pass


def get_recent_activity(limit: int = 10) -> List[Dict]:
    """Get recent actions from log files."""
    pass


def check_system_status() -> Dict[str, str]:
    """Check health of all system components."""
    pass


def get_approval_queue() -> List[Dict]:
    """Parse pending approval files."""
    pass


def calculate_completion_rate(date: str = "today") -> Dict:
    """Calculate task completion metrics."""
    pass


def get_daily_statistics() -> Dict:
    """Aggregate all daily statistics."""
    pass


def render_dashboard_section(template: str, data: Dict) -> str:
    """Render a dashboard section from template."""
    pass


def format_time_ago(timestamp: str) -> str:
    """Format timestamp as human-readable 'X minutes ago'."""
    pass


def get_icon_for_action(action: str) -> str:
    """Map action type to emoji icon."""
    pass
```

### Integration Points

**With Task Processor:**
```python
# In scripts/runner_silver.py
from scripts.dashboard_updater import update_dashboard

def process_tasks():
    # ... process tasks ...

    # Update dashboard after processing
    update_dashboard(trigger_event="task_processing_complete")
```

**With Email Handler:**
```python
# In scripts/email_handler.py
from scripts.dashboard_updater import update_dashboard

def draft_email(...):
    # ... create draft ...
    update_dashboard(trigger_event="email_draft_created")

def send_email_request(...):
    # ... create approval ...
    update_dashboard(trigger_event="email_approval_created")
```

**With Approval Executor:**
```python
# In scripts/approval_executor.py
from scripts.dashboard_updater import update_dashboard

def execute_approval(...):
    # ... execute action ...
    update_dashboard(trigger_event="approval_executed")
```

---

## ⚙️ Configuration

### Update Frequency

**File:** `config/dashboard_config.json`

```json
{
  "update_triggers": {
    "task_processed": true,
    "email_action": true,
    "approval_action": true,
    "file_event": false,
    "scheduled": true,
    "scheduled_interval": 300
  },
  "display_options": {
    "recent_activity_limit": 10,
    "show_weekly_summary": true,
    "show_performance_metrics": true,
    "show_rate_limits": true
  },
  "thresholds": {
    "approval_overdue_hours": 2,
    "high_priority_warning": 3,
    "degraded_status_minutes": 15
  },
  "icons": {
    "task_processed": "✓",
    "email_sent": "✓",
    "email_draft": "✓",
    "approval_created": "👤",
    "search_performed": "🔍",
    "categorization": "📊",
    "error": "❌",
    "warning": "⚠️"
  }
}
```

### Status Check Configuration

```json
{
  "status_checks": {
    "task_processor": {
      "check_method": "last_log_entry",
      "timeout_minutes": 10,
      "log_action": "process_task"
    },
    "email_handler": {
      "check_method": "last_log_entry",
      "timeout_minutes": 15,
      "log_action": "email_handler"
    },
    "mcp_gmail": {
      "check_method": "mcp_ping",
      "timeout_seconds": 30
    }
  }
}
```

---

## 🛡️ Error Handling

### 1. Missing Log Files

**Scenario:** Daily log file doesn't exist (new day, first run)

**Handling:**
```python
try:
    with open(log_file) as f:
        logs = json.load(f)
except FileNotFoundError:
    logs = []
    # Create placeholder dashboard with zero values
    return default_dashboard()
```

### 2. Corrupted Log File

**Scenario:** Log file is malformed JSON

**Handling:**
```python
try:
    logs = json.load(f)
except json.JSONDecodeError:
    log_error("dashboard_update_corrupted_log", {"file": log_file})
    # Use empty logs, continue with other data
    logs = []
```

### 3. Missing Dashboard.md

**Scenario:** Dashboard file doesn't exist (first run)

**Handling:**
```python
# Simply create new dashboard
# No error, this is expected on first run
with open(dashboard_path, "w") as f:
    f.write(render_dashboard(data))
```

### 4. Invalid Approval Files

**Scenario:** Approval file missing metadata or malformed

**Handling:**
```python
for approval_file in approval_files:
    try:
        metadata = parse_yaml_frontmatter(approval_file)
        # Process approval
    except Exception as e:
        log_warning("dashboard_update_invalid_approval", {
            "file": approval_file,
            "error": str(e)
        })
        # Skip this approval, continue with others
        continue
```

### 5. Component Status Unknown

**Scenario:** Cannot determine component status

**Handling:**
```python
try:
    status = check_component_status(component)
except Exception as e:
    # Default to unknown
    status = {
        'status': 'unknown',
        'icon': '⚪',
        'last_check': 'unavailable'
    }
```

---

## 📊 Success Criteria

Dashboard is working correctly when:

- ✅ Updates automatically after task processing
- ✅ Shows accurate task counts in real-time
- ✅ Recent activity reflects latest actions (<1 min delay)
- ✅ System status correctly identifies component health
- ✅ Approval queue lists all pending items with accurate ages
- ✅ Completion rates calculated correctly (matches log data)
- ✅ Today's statistics aggregate all metrics accurately
- ✅ Dashboard is readable and well-formatted
- ✅ Icons and status indicators display correctly
- ✅ Quick actions provide actionable next steps

---

## 🔗 Related Skills

### Current
- **Task Processor** - Triggers dashboard updates after processing
- **Email Handler** - Triggers updates after email actions
- **Approval Executor** - Triggers updates after approval execution

### Future
- **Dashboard API** - REST endpoint for dashboard data
- **Dashboard UI** - Web interface for visual dashboard
- **Alert System** - Notifications for critical dashboard metrics
- **Trend Analyzer** - Historical trend analysis and predictions

---

## 📞 Support

### Documentation
- **This Skill:** `AI_Employee_Vault/Skills/dashboard_updater/SKILL.md`
- **Implementation:** `scripts/dashboard_updater.py`
- **Templates:** Included in SKILL.md

### Testing
```bash
# Update dashboard manually
python scripts/dashboard_updater.py

# Check specific section
python -c "from scripts.dashboard_updater import count_tasks_by_folder; print(count_tasks_by_folder())"

# View current dashboard
cat AI_Employee_Vault/Dashboard.md
```

---

## 🚀 Roadmap

### Version 1.0 (Current)
- [x] Task counting
- [x] Recent activity feed
- [x] System status checks
- [x] Approval queue display
- [x] Completion rate calculation
- [x] Daily statistics

### Version 1.1 (Planned)
- [ ] Weekly/monthly summaries
- [ ] Trend analysis (up/down indicators)
- [ ] Performance graphs (ASCII or external)
- [ ] Custom dashboard layouts
- [ ] Alert thresholds
- [ ] Export to PDF

### Version 2.0 (Future)
- [ ] Web dashboard UI
- [ ] Real-time updates (WebSocket)
- [ ] Interactive charts
- [ ] Multi-user support
- [ ] Custom widgets
- [ ] Mobile app

---

**Skill Version:** 1.0.0
**Status:** Active ✓
**Last Updated:** February 2026
**Production Ready:** Yes
