#!/usr/bin/env python3
"""
CEO Weekly Briefing Generator
Analyzes completed tasks and generates executive summary report.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


VAULT_PATH = Path("./AI_Employee_Vault")
DONE_PATH = VAULT_PATH / "Done"
APPROVED_PATH = VAULT_PATH / "Approved"
REJECTED_PATH = VAULT_PATH / "Rejected"
HIGH_PRIORITY_PATH = VAULT_PATH / "High_Priority"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
LOGS_PATH = VAULT_PATH / "Logs"
REPORTS_PATH = VAULT_PATH / "Reports"


def get_date_range(days=7):
    """Get date range for the past N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def parse_task_metadata(file_path):
    """Parse metadata from task file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                metadata = {}
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                return metadata, parts[2].strip()
    except Exception:
        pass

    return {}, ""


def analyze_logs(days=7):
    """Analyze logs from the past N days."""
    start_date, end_date = get_date_range(days)

    stats = {
        "total_tasks": 0,
        "auto_completed": 0,
        "requires_approval": 0,
        "high_priority": 0,
        "errors": 0,
        "by_category": defaultdict(int),
        "by_priority": defaultdict(int),
        "daily_activity": defaultdict(int)
    }

    # Scan log files
    current_date = start_date
    while current_date <= end_date:
        log_file = LOGS_PATH / f"{current_date.strftime('%Y-%m-%d')}.json"

        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)

                day_key = current_date.strftime('%Y-%m-%d')

                for log_entry in logs:
                    action = log_entry.get("action", "")
                    details = log_entry.get("details", {})

                    stats["daily_activity"][day_key] += 1

                    if action == "auto_complete":
                        stats["auto_completed"] += 1
                        stats["total_tasks"] += 1
                    elif action == "requires_approval":
                        stats["requires_approval"] += 1
                        stats["total_tasks"] += 1
                    elif action == "high_priority":
                        stats["high_priority"] += 1
                        stats["total_tasks"] += 1
                    elif action == "categorized":
                        stats["total_tasks"] += 1
                    elif action == "error":
                        stats["errors"] += 1

                    # Track by category and priority
                    if isinstance(details, dict):
                        if "category" in details:
                            stats["by_category"][details["category"]] += 1
                        if "priority" in details:
                            stats["by_priority"][details["priority"]] += 1

            except Exception:
                pass

        current_date += timedelta(days=1)

    return stats


def scan_folder_tasks(folder_path):
    """Scan folder and return task summaries."""
    tasks = []

    if not folder_path.exists():
        return tasks

    for task_file in folder_path.glob("*.md"):
        metadata, content = parse_task_metadata(task_file)
        tasks.append({
            "name": task_file.name,
            "metadata": metadata,
            "summary": content[:150] + "..." if len(content) > 150 else content
        })

    return tasks


def generate_briefing(days=7):
    """Generate CEO weekly briefing."""
    print("Generating CEO Weekly Briefing...")

    # Ensure Reports directory exists
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)

    # Analyze logs
    stats = analyze_logs(days)

    # Scan folders for current state
    done_tasks = scan_folder_tasks(DONE_PATH)
    pending_tasks = scan_folder_tasks(PENDING_APPROVAL_PATH)
    high_priority_tasks = scan_folder_tasks(HIGH_PRIORITY_PATH)
    rejected_tasks = scan_folder_tasks(REJECTED_PATH)

    # Generate report
    start_date, end_date = get_date_range(days)
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_file = REPORTS_PATH / f"CEO_Briefing_{report_date}.md"

    report_content = f"""---
reportType: CEO Weekly Briefing
generatedAt: {datetime.now().isoformat()}
period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
---

# 📊 CEO Weekly Briefing
**Period:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## 🎯 Executive Summary

The AI Employee system processed **{stats['total_tasks']} tasks** over the past {days} days. Performance highlights:

- ✅ **{stats['auto_completed']} tasks** auto-completed without human intervention
- 🔒 **{stats['requires_approval']} tasks** flagged for approval
- ⚠️  **{stats['high_priority']} high-priority** tasks identified
- ❌ **{stats['errors']} errors** encountered

**Automation Rate:** {(stats['auto_completed'] / max(stats['total_tasks'], 1) * 100):.1f}%

---

## 📈 Activity Breakdown

### By Category
"""

    for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
        report_content += f"- **{category.replace('_', ' ').title()}**: {count} tasks\n"

    report_content += "\n### By Priority\n"
    for priority, count in sorted(stats['by_priority'].items(), key=lambda x: x[1], reverse=True):
        report_content += f"- **{priority.upper()}**: {count} tasks\n"

    report_content += "\n### Daily Activity\n"
    for day, count in sorted(stats['daily_activity'].items()):
        report_content += f"- **{day}**: {count} actions\n"

    report_content += f"""

---

## ⚠️  Items Requiring Attention

### Pending Approvals ({len(pending_tasks)})
"""

    if pending_tasks:
        for task in pending_tasks[:5]:  # Top 5
            report_content += f"\n**{task['name']}**\n"
            report_content += f"```\n{task['summary']}\n```\n"
    else:
        report_content += "\n✅ No pending approvals\n"

    report_content += f"""

### High Priority Tasks ({len(high_priority_tasks)})
"""

    if high_priority_tasks:
        for task in high_priority_tasks[:5]:  # Top 5
            report_content += f"\n**{task['name']}**\n"
            report_content += f"```\n{task['summary']}\n```\n"
    else:
        report_content += "\n✅ No high priority tasks pending\n"

    report_content += f"""

---

## ✅ Completed Tasks ({len(done_tasks)})

"""

    if done_tasks:
        for task in done_tasks[:10]:  # Top 10
            created_at = task['metadata'].get('createdAt', 'N/A')
            category = task['metadata'].get('category', 'unknown')
            report_content += f"- **{task['name']}** ({category}) - Completed: {created_at[:10]}\n"
    else:
        report_content += "No completed tasks in this period.\n"

    report_content += f"""

---

## 🚫 Rejected Tasks ({len(rejected_tasks)})

"""

    if rejected_tasks:
        for task in rejected_tasks[:5]:  # Top 5
            report_content += f"- **{task['name']}**\n"
    else:
        report_content += "No rejected tasks in this period.\n"

    report_content += f"""

---

## 📊 System Health

- **Total Folders Monitored:** 8
- **Active Tasks:** {len(high_priority_tasks) + len(pending_tasks)}
- **System Uptime:** Active
- **Error Rate:** {(stats['errors'] / max(stats['total_tasks'], 1) * 100):.1f}%

---

## 💡 Recommendations

"""

    # Generate smart recommendations
    recommendations = []

    if stats['auto_completed'] > stats['total_tasks'] * 0.6:
        recommendations.append("✅ High automation rate - system is performing efficiently")

    if stats['requires_approval'] > stats['total_tasks'] * 0.3:
        recommendations.append("⚠️  High approval rate - consider reviewing approval criteria")

    if stats['high_priority'] > 5:
        recommendations.append(f"⚠️  {stats['high_priority']} high-priority tasks - may need additional resources")

    if len(pending_tasks) > 10:
        recommendations.append(f"🔔 {len(pending_tasks)} tasks awaiting approval - review queue needed")

    if stats['errors'] > 0:
        recommendations.append(f"⚠️  {stats['errors']} errors detected - system diagnostics recommended")

    if not recommendations:
        recommendations.append("✅ System operating within normal parameters")

    for rec in recommendations:
        report_content += f"- {rec}\n"

    report_content += """

---

## 🎯 Next Steps

1. Review and approve/reject pending tasks
2. Address high-priority items
3. Monitor error logs for system issues
4. Evaluate automation effectiveness

---

*This report was automatically generated by the AI Employee System (Silver Tier)*
*For questions or concerns, please review the detailed logs in the Logs/ folder*

"""

    # Write report
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"[OK] Briefing generated: {report_file.name}")
    print(f"\nReport Summary:")
    print(f"  - Total tasks: {stats['total_tasks']}")
    print(f"  - Auto-completed: {stats['auto_completed']}")
    print(f"  - Pending approval: {len(pending_tasks)}")
    print(f"  - High priority: {len(high_priority_tasks)}")

    return report_file


if __name__ == "__main__":
    report = generate_briefing(days=7)
    print(f"\nReport saved to: {report}")
