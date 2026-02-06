#!/usr/bin/env python3
"""
Dashboard Updater Skill - Implementation
Maintains real-time Dashboard.md with task metrics and system status.

Version: 1.0.0
Author: AI Employee System
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_PATH = Path("./AI_Employee_Vault")
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
HIGH_PRIORITY_PATH = VAULT_PATH / "High_Priority"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
FAILED_PATH = VAULT_PATH / "Failed"
PLANS_PATH = VAULT_PATH / "Plans"
LOGS_PATH = VAULT_PATH / "Logs"
DASHBOARD_PATH = VAULT_PATH / "Dashboard.md"

# Configuration
RECENT_ACTIVITY_LIMIT = 10
APPROVAL_OVERDUE_HOURS = 2
HIGH_PRIORITY_WARNING_THRESHOLD = 3
COMPONENT_TIMEOUT_MINUTES = 15

# Icon mapping
ICONS = {
    "task_processed": "✓",
    "auto_complete": "✓",
    "high_priority": "⚠️",
    "approval_required": "👤",
    "email_sent": "✓",
    "email_draft": "✓",
    "search_performed": "🔍",
    "categorization": "📊",
    "error": "❌",
    "warning": "⚠️",
    "success": "✓"
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_directories():
    """Ensure all required directories exist."""
    for path in [NEEDS_ACTION_PATH, HIGH_PRIORITY_PATH, PENDING_APPROVAL_PATH,
                 APPROVED_PATH, DONE_PATH, FAILED_PATH, PLANS_PATH, LOGS_PATH]:
        path.mkdir(parents=True, exist_ok=True)


def log_action(action_type: str, details: Dict) -> None:
    """Log dashboard update action."""
    ensure_directories()

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "skill": "dashboard_updater",
        "action": action_type,
        **details
    }

    logs = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(log_entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as human-readable time ago."""
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        delta = now - timestamp

        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())} seconds ago"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(delta.total_seconds() / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
    except:
        return "unknown"


def parse_yaml_frontmatter(file_path: Path) -> Dict:
    """Parse YAML frontmatter from markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            return {}

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}

        # Simple YAML parser for basic key: value pairs
        metadata = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata
    except:
        return {}


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

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
    ensure_directories()

    counts = {
        'needs_action': len(list(NEEDS_ACTION_PATH.glob("*.md"))),
        'high_priority': len(list(HIGH_PRIORITY_PATH.glob("*.md"))),
        'pending_approval': len(list(PENDING_APPROVAL_PATH.glob("*.md"))),
        'approved': len(list(APPROVED_PATH.glob("*.md"))),
        'done': len(list(DONE_PATH.glob("*.md"))),
        'failed': len(list(FAILED_PATH.glob("*.md"))),
        'plans': len(list(PLANS_PATH.glob("*.md")))
    }

    return counts


def count_done_today() -> int:
    """Count tasks completed today."""
    today = datetime.now().strftime("%Y-%m-%d")
    count = 0

    for task_file in DONE_PATH.glob("*.md"):
        metadata = parse_yaml_frontmatter(task_file)
        processed_at = metadata.get('processedAt', '')

        if processed_at.startswith(today):
            count += 1

    return count


def get_recent_activity(limit: int = RECENT_ACTIVITY_LIMIT) -> List[Dict]:
    """
    Get recent actions from log files.

    Returns:
        [
            {
                'time': '17:28',
                'description': 'Task Processed: file.md → High Priority',
                'icon': '⚠️'
            },
            ...
        ]
    """
    ensure_directories()

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    if not log_file.exists():
        return []

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except json.JSONDecodeError:
        return []

    # Get last N entries
    recent_logs = logs[-limit:] if len(logs) > limit else logs

    # Format for display
    activity = []
    for log_entry in reversed(recent_logs):
        activity.append({
            'time': log_entry['timestamp'].split('T')[1][:5],  # HH:MM
            'description': format_log_description(log_entry),
            'icon': get_icon_for_log(log_entry)
        })

    return activity


def format_log_description(log_entry: Dict) -> str:
    """Format log entry for display."""
    action = log_entry.get('action', 'Unknown')
    skill = log_entry.get('skill', '')

    # Task processor actions
    if action == 'high_priority':
        filename = log_entry.get('file', 'unknown')
        return f"Task Processed: `{filename}` → High Priority"
    elif action == 'requires_approval':
        filename = log_entry.get('file', 'unknown')
        return f"Task Processed: `{filename}` → Pending Approval"
    elif action == 'auto_complete':
        filename = log_entry.get('file', 'unknown')
        return f"Task Processed: `{filename}` → Done (Auto)"
    elif action == 'categorized':
        filename = log_entry.get('file', 'unknown')
        return f"Task Processed: `{filename}` → Needs Action"

    # Email handler actions
    elif action == 'draft_email_success':
        recipient = log_entry.get('recipient', 'unknown')
        subject = log_entry.get('subject', 'No Subject')
        return f"Draft Created: {recipient} - {subject}"
    elif action == 'send_email_approval_created':
        recipient = log_entry.get('recipient', 'unknown')
        subject = log_entry.get('subject', 'No Subject')
        return f"Approval Created: Send email to {recipient}"
    elif action == 'email_sent':
        recipient = log_entry.get('recipient', 'unknown')
        subject = log_entry.get('subject', 'No Subject')
        return f"Email Sent: {recipient} - {subject}"
    elif action == 'search_emails_success':
        query = log_entry.get('query', 'unknown')
        count = log_entry.get('results_count', 0)
        return f"Search: {query} ({count} results)"
    elif action == 'categorize_emails_success':
        total = log_entry.get('total_emails', 0)
        urgent = log_entry.get('urgent', 0)
        needs_response = log_entry.get('needs_response', 0)
        return f"Email Categorized: {total} emails ({urgent} urgent, {needs_response} response)"

    # Generic
    else:
        return f"{action.replace('_', ' ').title()}"


def get_icon_for_log(log_entry: Dict) -> str:
    """Get icon for log entry."""
    action = log_entry.get('action', '')

    if 'high_priority' in action:
        return ICONS['high_priority']
    elif 'approval' in action:
        return ICONS['approval_required']
    elif 'auto_complete' in action or 'success' in action:
        return ICONS['success']
    elif 'email_sent' in action:
        return ICONS['email_sent']
    elif 'draft' in action:
        return ICONS['email_draft']
    elif 'search' in action:
        return ICONS['search_performed']
    elif 'categorize' in action:
        return ICONS['categorization']
    elif 'error' in action or 'failed' in action:
        return ICONS['error']
    elif 'warning' in action:
        return ICONS['warning']
    else:
        return ICONS['success']


def check_system_status() -> Dict[str, any]:
    """
    Check health of all system components.

    Returns:
        {
            'overall': 'operational',
            'components': {
                'task_processor': {'status': 'online', 'last_check': '2 min ago'},
                ...
            }
        }
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    components = {
        'task_processor': {'status': 'unknown', 'last_check': 'never'},
        'email_handler': {'status': 'unknown', 'last_check': 'never'},
        'approval_executor': {'status': 'unknown', 'last_check': 'never'},
        'mcp_servers': {'status': 'unknown', 'last_check': 'never'}
    }

    if not log_file.exists():
        return {'overall': 'unknown', 'components': components}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        return {'overall': 'unknown', 'components': components}

    # Check task processor
    task_logs = [l for l in logs if l.get('skill') == 'runner_silver' or 'task' in l.get('action', '')]
    if task_logs:
        last_log = task_logs[-1]
        last_time = datetime.fromisoformat(last_log['timestamp'])
        age_minutes = (datetime.now() - last_time).total_seconds() / 60

        if age_minutes < COMPONENT_TIMEOUT_MINUTES:
            components['task_processor']['status'] = 'online'
        else:
            components['task_processor']['status'] = 'idle'
        components['task_processor']['last_check'] = format_time_ago(last_log['timestamp'])

    # Check email handler
    email_logs = [l for l in logs if l.get('skill') == 'email_handler']
    if email_logs:
        last_log = email_logs[-1]
        last_time = datetime.fromisoformat(last_log['timestamp'])
        age_minutes = (datetime.now() - last_time).total_seconds() / 60

        if age_minutes < COMPONENT_TIMEOUT_MINUTES:
            components['email_handler']['status'] = 'online'
        else:
            components['email_handler']['status'] = 'idle'
        components['email_handler']['last_check'] = format_time_ago(last_log['timestamp'])

    # Check approval executor
    approval_logs = [l for l in logs if 'approval' in l.get('action', '') and l.get('skill') != 'email_handler']
    if approval_logs:
        last_log = approval_logs[-1]
        components['approval_executor']['status'] = 'ready'
        components['approval_executor']['last_check'] = format_time_ago(last_log['timestamp'])
    else:
        components['approval_executor']['status'] = 'ready'
        components['approval_executor']['last_check'] = 'idle'

    # MCP servers - assume connected if email handler is working
    if components['email_handler']['status'] == 'online':
        components['mcp_servers']['status'] = 'connected'
        components['mcp_servers']['last_check'] = components['email_handler']['last_check']
    else:
        components['mcp_servers']['status'] = 'unknown'

    # Determine overall status
    statuses = [c['status'] for c in components.values()]
    if all(s in ['online', 'ready', 'connected', 'idle'] for s in statuses):
        overall = 'operational'
    elif any(s == 'down' for s in statuses):
        overall = 'degraded'
    else:
        overall = 'operational'

    return {'overall': overall, 'components': components}


def get_approval_queue() -> List[Dict]:
    """
    Parse pending approval files.

    Returns:
        [
            {
                'action': 'Send Invoice Email',
                'recipient': 'client@example.com',
                'age_minutes': 30,
                'age_human': '30 minutes ago',
                'priority': 'medium',
                'file': 'send_invoice_approval.md',
                'overdue': False
            },
            ...
        ]
    """
    ensure_directories()

    approvals = []

    for approval_file in PENDING_APPROVAL_PATH.glob("*.md"):
        metadata = parse_yaml_frontmatter(approval_file)

        # Only include pending approvals
        if metadata.get('approval_status') == 'pending':
            created_at = metadata.get('created_at', '')

            if created_at:
                age = datetime.now() - datetime.fromisoformat(created_at)
                age_minutes = age.total_seconds() / 60
                overdue = age_minutes > (APPROVAL_OVERDUE_HOURS * 60)
            else:
                age_minutes = 0
                overdue = False

            # Extract action description
            action = extract_action_title(approval_file, metadata)

            # Extract recipient if email action
            recipient = None
            if 'mcp_params' in str(metadata):
                # Try to parse recipient from metadata
                recipient = metadata.get('to', metadata.get('recipient', ''))

            approvals.append({
                'action': action,
                'recipient': recipient,
                'age_minutes': age_minutes,
                'age_human': format_time_ago(created_at) if created_at else 'unknown',
                'priority': metadata.get('priority', 'medium'),
                'file': approval_file.name,
                'overdue': overdue
            })

    # Sort by age (oldest first)
    approvals.sort(key=lambda x: x['age_minutes'], reverse=True)

    return approvals


def extract_action_title(file_path: Path, metadata: Dict = None) -> str:
    """Extract action title from approval file."""
    if metadata is None:
        metadata = parse_yaml_frontmatter(file_path)

    # Try to get from metadata
    action = metadata.get('action', '')

    if action == 'send_email':
        subject = metadata.get('subject', '')
        if subject:
            return f"Send Email: {subject}"
        return "Send Email"

    # Try to extract from filename
    filename = file_path.stem
    filename = filename.replace('_', ' ')
    filename = filename.replace('send ', 'Send ')
    filename = filename.replace('approval', '').strip()

    return filename.title() if filename else "Approval Request"


def calculate_completion_rate(date: str = "today") -> Dict:
    """
    Calculate task completion metrics.

    Returns:
        {
            'total_processed': 17,
            'completed': 12,
            'auto_completed': 3,
            'high_priority': 2,
            'approval_required': 3,
            'failed': 0,
            'completion_rate': 70.6
        }
    """
    if date == "today":
        date = datetime.now().strftime("%Y-%m-%d")

    log_file = LOGS_PATH / f"{date}.json"

    if not log_file.exists():
        return {
            'total_processed': 0,
            'completed': 0,
            'auto_completed': 0,
            'high_priority': 0,
            'approval_required': 0,
            'failed': 0,
            'completion_rate': 0
        }

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        return {
            'total_processed': 0,
            'completed': 0,
            'auto_completed': 0,
            'high_priority': 0,
            'approval_required': 0,
            'failed': 0,
            'completion_rate': 0
        }

    # Count task processing actions
    task_logs = [l for l in logs if 'task' in l.get('action', '').lower() or
                 l.get('action') in ['high_priority', 'requires_approval', 'auto_complete', 'categorized']]

    total_processed = len(task_logs)
    completed = len([l for l in task_logs if l.get('success', True)])
    auto_completed = len([l for l in task_logs if l.get('action') == 'auto_complete'])
    high_priority = len([l for l in task_logs if l.get('action') == 'high_priority'])
    approval_required = len([l for l in task_logs if l.get('action') == 'requires_approval'])
    failed = len([l for l in task_logs if not l.get('success', True)])

    completion_rate = (completed / total_processed * 100) if total_processed > 0 else 0

    return {
        'total_processed': total_processed,
        'completed': completed,
        'auto_completed': auto_completed,
        'high_priority': high_priority,
        'approval_required': approval_required,
        'failed': failed,
        'completion_rate': round(completion_rate, 1)
    }


def get_daily_statistics() -> Dict:
    """
    Aggregate all daily statistics.

    Returns comprehensive stats for tasks, emails, rate limits, performance
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    stats = {
        'date': today,
        'tasks': calculate_completion_rate(today),
        'emails': {
            'drafts': 0,
            'sent': 0,
            'searches': 0,
            'categorized': 0
        },
        'rate_limits': {
            'send_email': {'used': 0, 'limit': 10, 'pct': 0},
            'draft_email': {'used': 0, 'limit': 50, 'pct': 0},
            'search_emails': {'used': 0, 'limit': 100, 'pct': 0}
        },
        'performance': {
            'avg_processing_time': 0,
            'success_rate': 100,
            'uptime_hours': 0
        }
    }

    if not log_file.exists():
        return stats

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        return stats

    # Count email actions
    stats['emails']['drafts'] = len([l for l in logs if l.get('action') == 'draft_email_success'])
    stats['emails']['sent'] = len([l for l in logs if l.get('action') == 'email_sent'])
    stats['emails']['searches'] = len([l for l in logs if l.get('action') == 'search_emails_success'])
    categorize_logs = [l for l in logs if l.get('action') == 'categorize_emails_success']
    if categorize_logs:
        stats['emails']['categorized'] = sum(l.get('total_emails', 0) for l in categorize_logs)

    # Load rate limits
    rate_limit_file = LOGS_PATH / "rate_limits.json"
    if rate_limit_file.exists():
        try:
            with open(rate_limit_file, "r", encoding="utf-8") as f:
                rate_data = json.load(f)

            for action in ['send_email', 'draft_email', 'search_emails']:
                if action in rate_data:
                    used = rate_data[action].get('count_today', 0)
                    limit = stats['rate_limits'][action]['limit']
                    pct = int((used / limit * 100)) if limit > 0 else 0

                    stats['rate_limits'][action]['used'] = used
                    stats['rate_limits'][action]['pct'] = pct
        except:
            pass

    # Calculate performance metrics
    task_logs = [l for l in logs if 'task' in l.get('action', '')]
    if task_logs:
        # Calculate success rate
        successful = len([l for l in task_logs if l.get('success', True)])
        stats['performance']['success_rate'] = round((successful / len(task_logs) * 100), 1)

        # Calculate uptime (time between first and last log)
        if len(logs) > 1:
            first_time = datetime.fromisoformat(logs[0]['timestamp'])
            last_time = datetime.fromisoformat(logs[-1]['timestamp'])
            uptime_hours = (last_time - first_time).total_seconds() / 3600
            stats['performance']['uptime_hours'] = round(uptime_hours, 2)

    return stats


# ============================================================================
# DASHBOARD RENDERING
# ============================================================================

def render_task_overview(counts: Dict, completion: Dict) -> str:
    """Render task overview section."""
    done_today = count_done_today()
    active_total = counts['needs_action'] + counts['high_priority'] + counts['pending_approval']

    # Determine status messages
    high_priority_status = "⚠️ Action Required" if counts['high_priority'] > 0 else "✓ Clear"
    if counts['pending_approval'] > 3:
        pending_status = "⚠️ Review Backlog"
    elif counts['pending_approval'] > 0:
        pending_status = "👤 Human Review Needed"
    else:
        pending_status = "✓ Clear"
    needs_action_status = "📋 Queued" if counts['needs_action'] > 0 else "✓ Clear"
    failed_status = "❌ Errors Present" if counts['failed'] > 0 else "✓ OK"

    return f"""## 📊 Task Overview

| Folder | Count | Status |
|--------|-------|--------|
| 🔴 High Priority | {counts['high_priority']} | {high_priority_status} |
| 🟡 Pending Approval | {counts['pending_approval']} | {pending_status} |
| 🔵 Needs Action | {counts['needs_action']} | {needs_action_status} |
| ✅ Done (Today) | {done_today} | ✓ Completed |
| ❌ Failed | {counts['failed']} | {failed_status} |

**Total Active Tasks:** {active_total}
**Completion Rate Today:** {completion['completion_rate']}% ({completion['completed']}/{completion['total_processed']})"""


def render_system_status(status_data: Dict) -> str:
    """Render system status section."""
    overall = status_data['overall']
    components = status_data['components']

    # Overall status
    if overall == 'operational':
        overall_icon = "🟢"
        overall_text = "OPERATIONAL"
        description = "All systems functioning normally"
    elif overall == 'degraded':
        overall_icon = "🟡"
        overall_text = "DEGRADED"
        description = "Some components experiencing issues"
    else:
        overall_icon = "⚪"
        overall_text = "UNKNOWN"
        description = "System status cannot be determined"

    # Component status icons
    def get_status_icon(status):
        return {
            'online': '🟢',
            'connected': '🟢',
            'ready': '🟢',
            'idle': '🟡',
            'degraded': '🟡',
            'down': '🔴',
            'offline': '🔴',
            'unknown': '⚪'
        }.get(status, '⚪')

    return f"""## 🎯 System Status

{overall_icon} **{overall_text}** - {description}

| Component | Status | Last Check |
|-----------|--------|------------|
| Task Processor | {get_status_icon(components['task_processor']['status'])} {components['task_processor']['status'].title()} | {components['task_processor']['last_check']} |
| Email Handler | {get_status_icon(components['email_handler']['status'])} {components['email_handler']['status'].title()} | {components['email_handler']['last_check']} |
| Approval Executor | {get_status_icon(components['approval_executor']['status'])} {components['approval_executor']['status'].title()} | {components['approval_executor']['last_check']} |
| MCP Servers | {get_status_icon(components['mcp_servers']['status'])} {components['mcp_servers']['status'].title()} | {components['mcp_servers']['last_check']} |"""


def render_approval_queue(approvals: List[Dict]) -> str:
    """Render approval queue section."""
    approval_count = len(approvals)
    overdue_count = len([a for a in approvals if a['overdue']])

    content = f"## 📋 Approval Queue\n\n**Items Awaiting Approval:** {approval_count}\n\n"

    if approval_count == 0:
        content += "✅ **No pending approvals** - All caught up!\n"
    else:
        for i, approval in enumerate(approvals[:10], 1):  # Show max 10
            recipient_text = f" - {approval['recipient']}" if approval['recipient'] else ""
            content += f"{i}. **{approval['action']}**{recipient_text}\n"
            content += f"   - Created: {approval['age_human']}\n"
            content += f"   - Priority: {approval['priority'].title()}\n"
            content += f"   - Action: `Pending_Approval/{approval['file']}`\n\n"

        if overdue_count > 0:
            content += f"⚠️ **{overdue_count} approval(s) overdue** (>{APPROVAL_OVERDUE_HOURS} hours old)\n"

    return content


def render_daily_statistics(stats: Dict) -> str:
    """Render daily statistics section."""
    date_obj = datetime.strptime(stats['date'], "%Y-%m-%d")
    date_formatted = date_obj.strftime("%B %d, %Y")

    tasks = stats['tasks']
    emails = stats['emails']
    rate_limits = stats['rate_limits']
    performance = stats['performance']

    # Calculate percentages
    def pct(value, total):
        return round((value / total * 100), 1) if total > 0 else 0

    total = tasks['total_processed']

    content = f"""## 📈 Today's Statistics

**Date:** {date_formatted}

### Task Processing
- **Total Processed:** {tasks['total_processed']} tasks
- **Auto-Completed:** {tasks['auto_completed']} tasks ({pct(tasks['auto_completed'], total)}%)
- **Routed to High Priority:** {tasks['high_priority']} tasks ({pct(tasks['high_priority'], total)}%)
- **Sent for Approval:** {tasks['approval_required']} tasks ({pct(tasks['approval_required'], total)}%)
- **Completed:** {tasks['completed']} tasks ({pct(tasks['completed'], total)}%)
- **Failed:** {tasks['failed']} tasks ({pct(tasks['failed'], total)}%)

### Email Activity
- **Drafts Created:** {emails['drafts']}
- **Emails Sent:** {emails['sent']}
- **Searches Performed:** {emails['searches']}
- **Emails Categorized:** {emails['categorized']}

### Rate Limits
- **Email Sends:** {rate_limits['send_email']['used']}/{rate_limits['send_email']['limit']} ({rate_limits['send_email']['pct']}% capacity)
- **Email Drafts:** {rate_limits['draft_email']['used']}/{rate_limits['draft_email']['limit']} ({rate_limits['draft_email']['pct']}% capacity)
- **Email Searches:** {rate_limits['search_emails']['used']}/{rate_limits['search_emails']['limit']} ({rate_limits['search_emails']['pct']}% capacity)

### Performance
- **Success Rate:** {performance['success_rate']}%
- **Uptime:** {performance['uptime_hours']} hours"""

    return content


def render_recent_activity(activity: List[Dict]) -> str:
    """Render recent activity section."""
    content = f"## 🔔 Recent Activity\n\n**Last {len(activity)} Actions:**\n\n"

    if not activity:
        content += "_No activity recorded today_\n"
    else:
        for i, item in enumerate(activity, 1):
            content += f"{i}. **{item['time']}** - {item['description']} {item['icon']}\n"

    return content


def render_quick_actions(counts: Dict, approvals: List[Dict]) -> str:
    """Render quick actions section."""
    content = "## 🚀 Quick Actions\n\n### For You\n"

    has_actions = False

    if counts['pending_approval'] > 0:
        content += f"- [ ] **Review {counts['pending_approval']} pending approval(s)** in `Pending_Approval/`\n"
        has_actions = True

    if counts['high_priority'] > 0:
        content += f"- [ ] **Address {counts['high_priority']} high priority task(s)** in `High_Priority/`\n"
        has_actions = True

    if counts['needs_action'] > 0:
        content += f"- [ ] **Process {counts['needs_action']} pending task(s)** in `Needs_Action/`\n"
        has_actions = True

    if not has_actions:
        content += "✅ **All caught up!** No immediate actions required.\n"

    content += "\n### Next Steps\n"

    if counts['pending_approval'] > 0:
        content += "1. Run approval executor: `python scripts/approval_executor.py`\n"

    if counts['high_priority'] > 0:
        # List high priority files
        hp_files = [f.stem for f in list(HIGH_PRIORITY_PATH.glob("*.md"))[:3]]
        if hp_files:
            content += f"2. Review high priority: {', '.join(f'`{f}.md`' for f in hp_files)}\n"

    overdue_approvals = [a for a in approvals if a['overdue']]
    if overdue_approvals:
        content += f"3. Check overdue approval(s): `{overdue_approvals[0]['file']}`\n"

    return content


# ============================================================================
# MAIN UPDATE FUNCTION
# ============================================================================

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
    ensure_directories()

    try:
        # Gather all data
        counts = count_tasks_by_folder()
        completion = calculate_completion_rate()
        system_status = check_system_status()
        approvals = get_approval_queue()
        statistics = get_daily_statistics()
        activity = get_recent_activity()

        # Render dashboard
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dashboard_content = f"""# AI Employee Dashboard

🤖 **Last Updated:** {updated_at}

---

{render_task_overview(counts, completion)}

---

{render_system_status(system_status)}

---

{render_approval_queue(approvals)}

---

{render_daily_statistics(statistics)}

---

{render_recent_activity(activity)}

---

{render_quick_actions(counts, approvals)}

---

**Dashboard Auto-Updates:** After every task processor run
**Manual Refresh:** Run `python scripts/dashboard_updater.py`
"""

        # Write to file
        with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
            f.write(dashboard_content)

        # Log update
        log_action("dashboard_updated", {
            "trigger_event": trigger_event or "manual",
            "updated_at": updated_at,
            "task_counts": counts,
            "approval_count": len(approvals),
            "success": True
        })

        return {
            "success": True,
            "updated_at": updated_at,
            "sections_updated": [
                "task_overview",
                "system_status",
                "approval_queue",
                "daily_statistics",
                "recent_activity",
                "quick_actions"
            ],
            "metrics": {
                "total_tasks": counts['needs_action'] + counts['high_priority'] + counts['pending_approval'],
                "completion_rate": completion['completion_rate'],
                "pending_approvals": len(approvals),
                "system_status": system_status['overall']
            }
        }

    except Exception as e:
        print(f"Error updating dashboard: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Dashboard Updater")
    print("=" * 60)

    result = update_dashboard(trigger_event="manual")

    if result['success']:
        print(f"\n[OK] Dashboard updated successfully!")
        print(f"Updated at: {result['updated_at']}")
        print(f"\nMetrics:")
        print(f"  - Total active tasks: {result['metrics']['total_tasks']}")
        print(f"  - Completion rate: {result['metrics']['completion_rate']}%")
        print(f"  - Pending approvals: {result['metrics']['pending_approvals']}")
        print(f"  - System status: {result['metrics']['system_status'].upper()}")
        print(f"\nDashboard location: {DASHBOARD_PATH}")
    else:
        print(f"\n[ERROR] Dashboard update failed: {result.get('error')}")
        sys.exit(1)
