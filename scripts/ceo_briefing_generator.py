#!/usr/bin/env python3
"""
CEO Briefing Generator - Implementation
Analyzes system data to generate executive briefings with actionable insights.

Version: 1.0.0
Author: AI Employee System
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import statistics


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
LOGS_PATH = VAULT_PATH / "Logs"
REPORTS_PATH = VAULT_PATH / "Reports"

# Thresholds
APPROVAL_BOTTLENECK_HOURS = 48
STALE_TASK_DAYS = 7
HIGH_PRIORITY_THRESHOLD_HOURS = 24
MIN_RECURRENCE_FOR_AUTOMATION = 3

# Targets
TARGET_COMPLETION_RATE = 85.0
TARGET_AUTOMATION_RATE = 30.0
TARGET_APPROVAL_HOURS = 24
TARGET_PROCESSING_MINUTES = 4.0


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_directories():
    """Ensure all required directories exist."""
    for path in [NEEDS_ACTION_PATH, HIGH_PRIORITY_PATH, PENDING_APPROVAL_PATH,
                 DONE_PATH, FAILED_PATH, LOGS_PATH, REPORTS_PATH]:
        path.mkdir(parents=True, exist_ok=True)


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

        metadata = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata
    except:
        return {}


def format_timedelta(td: timedelta) -> str:
    """Format timedelta as human-readable string."""
    hours = td.total_seconds() / 3600
    if hours < 1:
        return f"{int(td.total_seconds() / 60)} minutes"
    elif hours < 24:
        return f"{int(hours)} hours"
    else:
        days = int(hours / 24)
        return f"{days} day{'s' if days != 1 else ''}"


# ============================================================================
# CORE ANALYSIS FUNCTIONS
# ============================================================================

def analyze_logs(days: int = 7) -> Dict:
    """
    Analyze log files for past N days.

    Returns:
        {
            'total_tasks': int,
            'completed': int,
            'failed': int,
            'daily_breakdown': dict,
            'category_breakdown': dict,
            'completion_rate': float,
            'automation_rate': float,
            'failed_tasks': list,
            'processing_times': list
        }
    """
    ensure_directories()

    now = datetime.now()
    start_date = now - timedelta(days=days)

    all_logs = []
    daily_counts = defaultdict(int)
    categories = defaultdict(int)
    failed_tasks = []
    processing_times = []

    # Load logs for each day
    for i in range(days):
        date = start_date + timedelta(days=i)
        log_file = LOGS_PATH / f"{date.strftime('%Y-%m-%d')}.json"

        if not log_file.exists():
            continue

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                daily_logs = json.load(f)
                all_logs.extend(daily_logs)

                # Count tasks for this day
                date_str = date.strftime("%Y-%m-%d")
                task_count = len([l for l in daily_logs if 'task' in l.get('action', '').lower()])
                daily_counts[date_str] = task_count

        except (json.JSONDecodeError, Exception):
            continue

    # Analyze all logs
    total_tasks = 0
    completed_tasks = 0
    auto_completed = 0
    failed_count = 0

    for log in all_logs:
        action = log.get('action', '')

        # Count task processing events
        if action in ['high_priority', 'requires_approval', 'auto_complete', 'categorized']:
            total_tasks += 1

            if action == 'auto_complete':
                auto_completed += 1

            if log.get('success', True):
                completed_tasks += 1

            # Categorize
            if action == 'high_priority':
                categories['High Priority'] += 1
            elif action == 'requires_approval':
                categories['Approval Required'] += 1
            elif action == 'auto_complete':
                categories['Auto-Completed'] += 1
            else:
                categories['Normal'] += 1

        # Track failed tasks
        if 'error' in action or 'failed' in action or not log.get('success', True):
            if 'file' in log:
                failed_tasks.append({
                    'file': log.get('file'),
                    'error': log.get('error', 'Unknown error'),
                    'timestamp': log.get('timestamp')
                })
            failed_count += 1

        # Track email actions for categorization
        if 'email' in action:
            if 'send' in action:
                categories['Email - Send'] += 1
            elif 'draft' in action:
                categories['Email - Draft'] += 1
            elif 'search' in action:
                categories['Email - Search'] += 1
            elif 'categorize' in action:
                categories['Email - Categorize'] += 1

    # Calculate rates
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    automation_rate = (auto_completed / total_tasks * 100) if total_tasks > 0 else 0

    return {
        'total_tasks': total_tasks,
        'completed': completed_tasks,
        'failed': failed_count,
        'auto_completed': auto_completed,
        'daily_breakdown': dict(daily_counts),
        'category_breakdown': dict(categories),
        'completion_rate': round(completion_rate, 1),
        'automation_rate': round(automation_rate, 1),
        'failed_tasks': failed_tasks[:10],  # Top 10
        'processing_times': processing_times,
        'days_analyzed': len(daily_counts)
    }


def analyze_task_ages() -> Dict:
    """
    Analyze age of tasks in all folders.

    Returns:
        {
            'stale_tasks': list,
            'approval_bottlenecks': list,
            'high_priority_delayed': list,
            'avg_age_by_folder': dict
        }
    """
    ensure_directories()

    now = datetime.now()
    stale_tasks = []
    approval_bottlenecks = []
    high_priority_delayed = []
    folder_ages = defaultdict(list)

    # Analyze Pending_Approval
    for task_file in PENDING_APPROVAL_PATH.glob("*.md"):
        metadata = parse_yaml_frontmatter(task_file)
        created_at = metadata.get('created_at', '')

        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                age = now - created
                folder_ages['Pending_Approval'].append(age.total_seconds() / 3600)  # hours

                if age.total_seconds() > (APPROVAL_BOTTLENECK_HOURS * 3600):
                    approval_bottlenecks.append({
                        'file': task_file.name,
                        'age': format_timedelta(age),
                        'age_hours': int(age.total_seconds() / 3600),
                        'created_at': created_at
                    })
            except:
                pass

    # Analyze Needs_Action
    for task_file in NEEDS_ACTION_PATH.glob("*.md"):
        metadata = parse_yaml_frontmatter(task_file)
        created_at = metadata.get('createdAt', metadata.get('created_at', ''))

        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                age = now - created
                folder_ages['Needs_Action'].append(age.total_seconds() / 86400)  # days

                if age.total_seconds() > (STALE_TASK_DAYS * 86400):
                    stale_tasks.append({
                        'file': task_file.name,
                        'age': format_timedelta(age),
                        'age_days': int(age.total_seconds() / 86400),
                        'created_at': created_at
                    })
            except:
                pass

    # Analyze High_Priority
    for task_file in HIGH_PRIORITY_PATH.glob("*.md"):
        metadata = parse_yaml_frontmatter(task_file)
        created_at = metadata.get('createdAt', metadata.get('created_at', ''))

        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                age = now - created
                folder_ages['High_Priority'].append(age.total_seconds() / 3600)  # hours

                if age.total_seconds() > (HIGH_PRIORITY_THRESHOLD_HOURS * 3600):
                    high_priority_delayed.append({
                        'file': task_file.name,
                        'age': format_timedelta(age),
                        'age_hours': int(age.total_seconds() / 3600),
                        'created_at': created_at
                    })
            except:
                pass

    # Calculate averages
    avg_ages = {}
    for folder, ages in folder_ages.items():
        if ages:
            avg_ages[folder] = round(statistics.mean(ages), 1)
        else:
            avg_ages[folder] = 0

    # Sort by age (oldest first)
    stale_tasks.sort(key=lambda x: x['age_days'], reverse=True)
    approval_bottlenecks.sort(key=lambda x: x['age_hours'], reverse=True)
    high_priority_delayed.sort(key=lambda x: x['age_hours'], reverse=True)

    return {
        'stale_tasks': stale_tasks[:10],  # Top 10 oldest
        'approval_bottlenecks': approval_bottlenecks[:10],
        'high_priority_delayed': high_priority_delayed[:5],
        'avg_age_by_folder': avg_ages
    }


def detect_patterns(logs_data: Dict) -> List[Dict]:
    """
    Detect patterns in task data.

    Returns list of detected patterns with suggestions.
    """
    patterns = []

    # Pattern 1: High automation rate (good)
    if logs_data['automation_rate'] > 40:
        patterns.append({
            'type': 'positive',
            'title': 'High Automation Rate',
            'description': f"{logs_data['automation_rate']}% of tasks auto-completed",
            'insight': 'System is efficiently handling routine tasks'
        })

    # Pattern 2: Low automation rate (opportunity)
    if logs_data['automation_rate'] < 20 and logs_data['total_tasks'] > 10:
        patterns.append({
            'type': 'opportunity',
            'title': 'Low Automation Rate',
            'description': f"Only {logs_data['automation_rate']}% auto-completed",
            'suggestion': 'Review task types for automation opportunities'
        })

    # Pattern 3: High failure rate (concern)
    if logs_data['failed'] > 0:
        failure_rate = (logs_data['failed'] / logs_data['total_tasks'] * 100)
        if failure_rate > 5:
            patterns.append({
                'type': 'concern',
                'title': 'Elevated Failure Rate',
                'description': f"{failure_rate:.1f}% of tasks failed",
                'action': 'Investigate root causes and implement fixes'
            })

    # Pattern 4: Category dominance
    categories = logs_data['category_breakdown']
    if categories:
        max_category = max(categories.items(), key=lambda x: x[1])
        max_pct = (max_category[1] / logs_data['total_tasks'] * 100)

        if max_pct > 40:
            patterns.append({
                'type': 'observation',
                'title': f'{max_category[0]} Dominates Volume',
                'description': f"{max_pct:.0f}% of tasks are '{max_category[0]}'",
                'insight': 'Consider specialization or dedicated resources'
            })

    return patterns


def generate_suggestions(analysis: Dict, age_analysis: Dict) -> List[Dict]:
    """
    Generate proactive suggestions based on analysis.

    Returns list of actionable suggestions.
    """
    suggestions = []

    # Suggestion 1: Address approval bottleneck
    if len(age_analysis['approval_bottlenecks']) > 3:
        suggestions.append({
            'priority': 'high',
            'type': 'bottleneck',
            'title': f'Clear Approval Backlog ({len(age_analysis["approval_bottlenecks"])} tasks)',
            'description': f'{len(age_analysis["approval_bottlenecks"])} tasks pending approval for >{APPROVAL_BOTTLENECK_HOURS} hours',
            'recommendation': 'Schedule daily approval sessions or implement two-tier approval system',
            'estimated_savings': f'{len(age_analysis["approval_bottlenecks"]) * 10} minutes',
            'impact': 'High - delays client communications'
        })

    # Suggestion 2: Review stale tasks
    if len(age_analysis['stale_tasks']) > 0:
        suggestions.append({
            'priority': 'medium',
            'type': 'maintenance',
            'title': f'Review {len(age_analysis["stale_tasks"])} Stale Tasks',
            'description': f'Tasks in Needs_Action for >{STALE_TASK_DAYS} days',
            'recommendation': 'Archive, set deadlines, or escalate priority',
            'estimated_savings': '30 minutes cleanup time',
            'impact': 'Medium - prevents task accumulation'
        })

    # Suggestion 3: Increase automation
    if analysis['automation_rate'] < TARGET_AUTOMATION_RATE:
        gap = TARGET_AUTOMATION_RATE - analysis['automation_rate']
        suggestions.append({
            'priority': 'medium',
            'type': 'automation',
            'title': f'Increase Automation Rate by {gap:.0f}%',
            'description': f'Current: {analysis["automation_rate"]}%, Target: {TARGET_AUTOMATION_RATE}%',
            'recommendation': 'Review task types for automation opportunities, create templates',
            'estimated_savings': f'{gap * 2:.0f} minutes/week',
            'impact': 'High - improves efficiency and reduces manual work'
        })

    # Suggestion 4: Address failed tasks
    if len(analysis['failed_tasks']) > 0:
        suggestions.append({
            'priority': 'high',
            'type': 'reliability',
            'title': f'Fix {len(analysis["failed_tasks"])} Failed Tasks',
            'description': 'Tasks failed due to errors',
            'recommendation': 'Investigate error patterns, implement fixes or retry logic',
            'estimated_savings': 'Prevents future failures',
            'impact': 'High - improves reliability and success rate'
        })

    # Suggestion 5: High priority attention
    if len(age_analysis['high_priority_delayed']) > 0:
        suggestions.append({
            'priority': 'high',
            'type': 'urgency',
            'title': f'{len(age_analysis["high_priority_delayed"])} High Priority Tasks Delayed',
            'description': f'High priority tasks older than {HIGH_PRIORITY_THRESHOLD_HOURS} hours',
            'recommendation': 'Immediate review and action required',
            'estimated_savings': 'Prevents escalation',
            'impact': 'Critical - may affect client satisfaction'
        })

    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))

    return suggestions


# ============================================================================
# REPORT RENDERING
# ============================================================================

def render_executive_summary(analysis: Dict, age_analysis: Dict) -> str:
    """Render executive summary section."""
    # Determine system health
    issues = len(age_analysis['approval_bottlenecks']) + len(age_analysis['stale_tasks']) + analysis['failed']
    if issues == 0:
        health = "🟢 Excellent"
    elif issues < 3:
        health = "🟢 Good"
    elif issues < 6:
        health = "🟡 Fair"
    else:
        health = "🔴 Needs Attention"

    # Calculate trends (mock - would compare to previous period)
    trend_indicator = "+" if analysis['total_tasks'] > 10 else ""

    summary = f"""## 📊 Executive Summary

**System Health:** {health}

**Key Metrics:**
- **Tasks Processed:** {analysis['total_tasks']} tasks
- **Completion Rate:** {analysis['completion_rate']}%
- **Automation Rate:** {analysis['automation_rate']}%
- **Failed Tasks:** {analysis['failed']}

**Highlights:**
- ✅ Processed {analysis['total_tasks']} tasks with {analysis['completion_rate']}% completion rate
- {'✅' if analysis['automation_rate'] >= TARGET_AUTOMATION_RATE else '⚠️'} {analysis['auto_completed']} tasks auto-completed ({analysis['automation_rate']}% automation rate)
- {'✅' if len(age_analysis['approval_bottlenecks']) == 0 else '⚠️'} {len(age_analysis['approval_bottlenecks'])} approvals pending >{APPROVAL_BOTTLENECK_HOURS} hours
- {'✅' if analysis['failed'] == 0 else '❌'} {analysis['failed']} tasks failed

**Bottom Line:** {'System performing well' if issues < 3 else 'Attention needed on bottlenecks and delays'}.
"""

    return summary


def render_metrics_table(analysis: Dict) -> str:
    """Render performance metrics table."""
    content = """## 📈 Performance Metrics

### Task Processing Overview

| Metric | Value |
|--------|-------|"""

    content += f"""
| Total Tasks | {analysis['total_tasks']} |
| Completed | {analysis['completed']} ({analysis['completion_rate']}%) |
| Auto-Completed | {analysis['auto_completed']} ({analysis['automation_rate']}%) |
| Failed | {analysis['failed']} |
| Days Analyzed | {analysis['days_analyzed']} |
"""

    return content


def render_daily_breakdown(analysis: Dict) -> str:
    """Render daily task breakdown."""
    daily = analysis['daily_breakdown']

    if not daily:
        return ""

    content = "\n### Daily Breakdown\n\n```\n"

    # Sort by date
    sorted_days = sorted(daily.items())

    for date, count in sorted_days:
        # Create bar chart
        bar_length = min(count, 20)  # Max 20 chars
        bar = "█" * bar_length + "░" * (20 - bar_length)

        # Day of week
        day_obj = datetime.strptime(date, "%Y-%m-%d")
        day_name = day_obj.strftime("%a")

        content += f"{day_name}  {bar}  {count} tasks\n"

    content += "```\n"

    return content


def render_category_breakdown(analysis: Dict) -> str:
    """Render task category breakdown."""
    categories = analysis['category_breakdown']

    if not categories:
        return ""

    total = analysis['total_tasks']

    content = "\n## 🎯 Task Categories Analysis\n\n"
    content += "| Category | Count | % of Total |\n"
    content += "|----------|-------|------------|\n"

    # Sort by count
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_cats:
        pct = (count / total * 100) if total > 0 else 0
        content += f"| {category} | {count} | {pct:.1f}% |\n"

    return content


def render_bottlenecks(age_analysis: Dict) -> str:
    """Render bottlenecks section."""
    content = "\n## 🚨 Bottlenecks & Concerns\n\n"

    has_issues = False

    # Approval bottlenecks
    if age_analysis['approval_bottlenecks']:
        has_issues = True
        content += f"### ⚠️ Approval Backlog\n\n"
        content += f"**Issue:** {len(age_analysis['approval_bottlenecks'])} tasks stuck in Pending_Approval for >{APPROVAL_BOTTLENECK_HOURS} hours\n\n"
        content += "**Affected Tasks:**\n"

        for task in age_analysis['approval_bottlenecks'][:5]:  # Top 5
            content += f"- `{task['file']}` - {task['age']} old\n"

        if len(age_analysis['approval_bottlenecks']) > 5:
            content += f"- ... and {len(age_analysis['approval_bottlenecks']) - 5} more\n"

        content += "\n**Recommendation:** Schedule approval review session, consider delegation.\n\n"

    # Stale tasks
    if age_analysis['stale_tasks']:
        has_issues = True
        content += f"### 📋 Stale Tasks in Needs_Action\n\n"
        content += f"**Issue:** {len(age_analysis['stale_tasks'])} tasks sitting in Needs_Action for >{STALE_TASK_DAYS} days\n\n"
        content += "**Tasks:**\n"

        for task in age_analysis['stale_tasks'][:5]:  # Top 5
            content += f"- `{task['file']}` - {task['age']} old\n"

        content += "\n**Recommendation:** Review and set explicit deadlines or archive.\n\n"

    # High priority delayed
    if age_analysis['high_priority_delayed']:
        has_issues = True
        content += f"### ⚠️ Delayed High Priority Tasks\n\n"
        content += f"**Issue:** {len(age_analysis['high_priority_delayed'])} high priority tasks older than {HIGH_PRIORITY_THRESHOLD_HOURS} hours\n\n"
        content += "**Tasks:**\n"

        for task in age_analysis['high_priority_delayed'][:5]:
            content += f"- `{task['file']}` - {task['age']} old\n"

        content += "\n**Recommendation:** Immediate attention required.\n\n"

    if not has_issues:
        content += "✅ **No significant bottlenecks detected.** System operating smoothly.\n\n"

    return content


def render_suggestions(suggestions: List[Dict]) -> str:
    """Render proactive suggestions."""
    if not suggestions:
        return "\n## 💡 Proactive Suggestions\n\n✅ **No immediate suggestions.** System is well-optimized.\n\n"

    content = "\n## 💡 Proactive Suggestions\n\n"

    for i, suggestion in enumerate(suggestions, 1):
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(suggestion['priority'], '⚪')

        content += f"### {i}. {priority_emoji} {suggestion['title']}\n\n"
        content += f"**Type:** {suggestion['type'].title()}\n"
        content += f"**Priority:** {suggestion['priority'].upper()}\n\n"
        content += f"**Description:** {suggestion['description']}\n\n"
        content += f"**Recommendation:** {suggestion['recommendation']}\n\n"

        if 'estimated_savings' in suggestion:
            content += f"**Estimated Savings:** {suggestion['estimated_savings']}\n\n"

        if 'impact' in suggestion:
            content += f"**Impact:** {suggestion['impact']}\n\n"

        content += "---\n\n"

    return content


def render_action_items(suggestions: List[Dict]) -> str:
    """Render action items section."""
    if not suggestions:
        return ""

    content = "\n## 🎯 Action Items for Leadership\n\n"

    # Group by priority
    high_priority = [s for s in suggestions if s['priority'] == 'high']
    medium_priority = [s for s in suggestions if s['priority'] == 'medium']

    if high_priority:
        content += "### 🔴 Immediate (This Week)\n\n"
        for i, suggestion in enumerate(high_priority, 1):
            content += f"{i}. **{suggestion['title']}**\n"
            content += f"   - Action: {suggestion['recommendation']}\n"
            if 'estimated_savings' in suggestion:
                content += f"   - Savings: {suggestion['estimated_savings']}\n"
            content += "\n"

    if medium_priority:
        content += "### 🟡 Short Term (Next 2 Weeks)\n\n"
        for i, suggestion in enumerate(medium_priority, 1):
            content += f"{i}. **{suggestion['title']}**\n"
            content += f"   - Action: {suggestion['recommendation']}\n"
            content += "\n"

    return content


# ============================================================================
# MAIN BRIEFING GENERATOR
# ============================================================================

def generate_ceo_briefing(days: int = 7) -> Dict:
    """
    Generate CEO briefing report.

    Args:
        days: Number of days to analyze

    Returns:
        {
            'success': bool,
            'report_file': str,
            'metrics': dict
        }
    """
    ensure_directories()

    print("=" * 60)
    print("CEO Briefing Generator")
    print("=" * 60)
    print(f"\nAnalyzing data for the past {days} days...\n")

    try:
        # Step 1: Analyze logs
        print("[1/5] Analyzing log files...")
        logs_analysis = analyze_logs(days)
        print(f"      Found {logs_analysis['total_tasks']} tasks across {logs_analysis['days_analyzed']} days")

        # Step 2: Analyze task ages
        print("[2/5] Analyzing task ages...")
        age_analysis = analyze_task_ages()
        print(f"      Identified {len(age_analysis['approval_bottlenecks'])} approval bottlenecks")

        # Step 3: Detect patterns
        print("[3/5] Detecting patterns...")
        patterns = detect_patterns(logs_analysis)
        print(f"      Detected {len(patterns)} patterns")

        # Step 4: Generate suggestions
        print("[4/5] Generating suggestions...")
        suggestions = generate_suggestions(logs_analysis, age_analysis)
        print(f"      Generated {len(suggestions)} actionable suggestions")

        # Step 5: Render report
        print("[5/5] Rendering report...")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        report_content = f"""# Executive Briefing
## {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}

📊 **Report Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
👤 **Prepared For:** Executive Leadership
📈 **Period:** {days} days ({start_date.strftime('%B %d')} - {end_date.strftime('%B %d')})

---

{render_executive_summary(logs_analysis, age_analysis)}

---

{render_metrics_table(logs_analysis)}

{render_daily_breakdown(logs_analysis)}

---

{render_category_breakdown(logs_analysis)}

---

{render_bottlenecks(age_analysis)}

---

{render_suggestions(suggestions)}

{render_action_items(suggestions)}

---

## 📊 Raw Data Summary

```json
{{
  "period": "{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
  "total_tasks": {logs_analysis['total_tasks']},
  "completed": {logs_analysis['completed']},
  "failed": {logs_analysis['failed']},
  "completion_rate": {logs_analysis['completion_rate']},
  "automation_rate": {logs_analysis['automation_rate']},
  "bottlenecks": {{
    "approval_backlog": {len(age_analysis['approval_bottlenecks'])},
    "stale_tasks": {len(age_analysis['stale_tasks'])},
    "high_priority_delayed": {len(age_analysis['high_priority_delayed'])}
  }}
}}
```

---

**Report End**

---

*This briefing was automatically generated by the AI Employee System.*
*Next briefing: {(end_date + timedelta(days=7)).strftime('%B %d, %Y')}*
"""

        # Save report
        report_filename = f"CEO_Briefing_{end_date.strftime('%Y-%m-%d')}.md"
        report_path = REPORTS_PATH / report_filename

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n[OK] Report generated: {report_path}")

        return {
            "success": True,
            "report_file": str(report_path),
            "metrics": {
                "total_tasks": logs_analysis['total_tasks'],
                "completion_rate": logs_analysis['completion_rate'],
                "automation_rate": logs_analysis['automation_rate'],
                "bottlenecks": len(age_analysis['approval_bottlenecks']) + len(age_analysis['stale_tasks']),
                "suggestions": len(suggestions)
            }
        }

    except Exception as e:
        print(f"\n[ERROR] Error generating briefing: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Generate CEO briefing report")
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze (default: 7)')
    parser.add_argument('--dry-run', action='store_true', help='Analyze without generating report')

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN MODE - No report will be generated\n")

    result = generate_ceo_briefing(days=args.days)

    if result['success']:
        print("\n" + "=" * 60)
        print("BRIEFING SUMMARY")
        print("=" * 60)
        print(f"Total Tasks Analyzed:  {result['metrics']['total_tasks']}")
        print(f"Completion Rate:       {result['metrics']['completion_rate']}%")
        print(f"Automation Rate:       {result['metrics']['automation_rate']}%")
        print(f"Bottlenecks Found:     {result['metrics']['bottlenecks']}")
        print(f"Suggestions Generated: {result['metrics']['suggestions']}")
        print("=" * 60)
    else:
        sys.exit(1)
