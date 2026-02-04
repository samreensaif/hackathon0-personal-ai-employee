#!/usr/bin/env python3
"""
Silver Tier Runner Script for AI Employee System
Enhanced with priority categorization, auto-completion, and intelligent routing.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path


VAULT_PATH = Path("./AI_Employee_Vault")
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
HIGH_PRIORITY_PATH = VAULT_PATH / "High_Priority"
DONE_PATH = VAULT_PATH / "Done"
PLANS_PATH = VAULT_PATH / "Plans"
LOGS_PATH = VAULT_PATH / "Logs"

# Keywords that require human approval (sensitive actions)
APPROVAL_KEYWORDS = [
    "email", "message", "whatsapp", "contact",
    "payment", "money", "bank", "transfer",
    "send", "reply", "respond", "purchase", "buy",
    "delete", "remove", "cancel", "refund"
]

# High priority keywords
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "asap", "critical", "emergency",
    "deadline", "important", "priority", "immediate",
    "today", "now", "escalate"
]

# Low priority keywords (can auto-complete)
LOW_PRIORITY_KEYWORDS = [
    "reminder", "note", "fyi", "info", "read",
    "review", "check", "later", "when possible",
    "low priority", "optional"
]

# Auto-completable task types (simple, non-sensitive)
AUTO_COMPLETE_KEYWORDS = [
    "reminder", "note", "fyi", "read later",
    "bookmark", "save", "archive"
]


def log_action(action_type, file_name, details=None):
    """Log action to daily JSON log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,
        "file": file_name
    }

    if details:
        log_entry["details"] = details

    # Read existing logs
    logs = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    # Append new log
    logs.append(log_entry)

    # Write back
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def read_task_content(file_path):
    """Read task file and extract content (skip metadata if present)."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip metadata block if present
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()

    return content.strip()


def update_task_metadata(file_path, new_fields):
    """Update metadata fields in task file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse existing metadata
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata_lines = parts[1].strip().split("\n")
            task_content = parts[2]

            # Parse existing metadata into dict
            metadata = {}
            for line in metadata_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

            # Update with new fields
            metadata.update(new_fields)

            # Rebuild metadata block
            new_metadata = "---\n"
            for key, value in metadata.items():
                new_metadata += f"{key}: {value}\n"
            new_metadata += "---\n"

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_metadata + task_content)

            return True

    return False


def requires_approval(task_content):
    """Check if task content contains keywords requiring approval."""
    content_lower = task_content.lower()
    return any(keyword in content_lower for keyword in APPROVAL_KEYWORDS)


def is_high_priority(task_content):
    """Check if task is high priority."""
    content_lower = task_content.lower()
    return any(keyword in content_lower for keyword in HIGH_PRIORITY_KEYWORDS)


def is_low_priority(task_content):
    """Check if task is low priority."""
    content_lower = task_content.lower()
    return any(keyword in content_lower for keyword in LOW_PRIORITY_KEYWORDS)


def can_auto_complete(task_content):
    """Check if task can be auto-completed without human intervention."""
    content_lower = task_content.lower()

    # Must be low priority AND contain auto-complete keywords
    # AND NOT require approval
    is_auto_completable = any(keyword in content_lower for keyword in AUTO_COMPLETE_KEYWORDS)
    needs_approval = requires_approval(task_content)

    return is_auto_completable and not needs_approval


def categorize_task(task_content):
    """Categorize task and return category."""
    if requires_approval(task_content):
        return "approval_required"
    elif can_auto_complete(task_content):
        return "auto_complete"
    elif is_high_priority(task_content):
        return "high_priority"
    elif is_low_priority(task_content):
        return "low_priority"
    else:
        return "normal"


def create_plan(task_name, task_content, category, priority):
    """Create a plan file with checkbox steps."""
    plan_name = Path(task_name).stem + "_plan.md"
    plan_path = PLANS_PATH / plan_name

    timestamp = datetime.now().isoformat()

    # Generate plan steps based on category
    if category == "auto_complete":
        steps = [
            "- [x] Task received and categorized",
            "- [x] Identified as auto-completable",
            "- [x] Moved to Done automatically",
            "- [x] Task archived"
        ]
    elif category == "high_priority":
        steps = [
            "- [ ] URGENT: Analyze task requirements immediately",
            "- [ ] Identify critical dependencies",
            "- [ ] Execute high-priority actions",
            "- [ ] Verify critical outcomes",
            "- [ ] Notify stakeholders",
            "- [ ] Document results"
        ]
    elif category == "approval_required":
        steps = [
            "- [ ] Analyze sensitive action requirements",
            "- [ ] Prepare approval request",
            "- [ ] Wait for human approval",
            "- [ ] Execute approved actions",
            "- [ ] Verify outcomes",
            "- [ ] Document and log actions"
        ]
    else:
        steps = [
            "- [ ] Analyze task requirements",
            "- [ ] Gather necessary information",
            "- [ ] Break down task into subtasks",
            "- [ ] Execute primary actions",
            "- [ ] Verify results",
            "- [ ] Document outcomes",
            "- [ ] Update task status"
        ]

    plan_content = f"""---
taskFile: {task_name}
createdAt: {timestamp}
category: {category}
priority: {priority}
requiresApproval: {category == 'approval_required'}
autoCompleted: {category == 'auto_complete'}
status: {'completed' if category == 'auto_complete' else 'pending'}
---

# Execution Plan: {Path(task_name).stem}

**Priority:** {priority.upper()}
**Category:** {category.replace('_', ' ').title()}

## Task Summary
{task_content[:300]}{'...' if len(task_content) > 300 else ''}

## Execution Steps
{chr(10).join(steps)}

## Notes
- This plan was automatically generated
{'- ✅ **AUTO-COMPLETED** - Simple task, no action required' if category == 'auto_complete' else ''}
{'- ⚠️ **HIGH PRIORITY** - Requires immediate attention' if category == 'high_priority' else ''}
{'- 🔒 **REQUIRES HUMAN APPROVAL** before execution' if category == 'approval_required' else ''}
{'- 📋 Standard priority task' if category == 'normal' else ''}

## Execution Log
{f'Auto-completed at {timestamp}' if category == 'auto_complete' else '_Will be populated during execution_'}
"""

    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(plan_content)

    return plan_name


def move_task(task_file, destination_path, category):
    """Move task file to appropriate folder."""
    dest = destination_path / task_file.name

    # Update metadata before moving
    update_task_metadata(task_file, {
        "category": category,
        "processedAt": datetime.now().isoformat()
    })

    shutil.move(str(task_file), str(dest))
    return dest


def process_tasks():
    """Process all tasks in Needs_Action folder with Silver Tier intelligence."""
    # Ensure directories exist
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
    PENDING_APPROVAL_PATH.mkdir(parents=True, exist_ok=True)
    HIGH_PRIORITY_PATH.mkdir(parents=True, exist_ok=True)
    DONE_PATH.mkdir(parents=True, exist_ok=True)
    PLANS_PATH.mkdir(parents=True, exist_ok=True)
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    stats = {
        "processed": 0,
        "auto_completed": 0,
        "high_priority": 0,
        "pending_approval": 0,
        "normal": 0
    }

    print("=" * 60)
    print("SILVER TIER AI EMPLOYEE - Task Runner")
    print("=" * 60)
    print(f"Processing tasks in: {NEEDS_ACTION_PATH.absolute()}\n")

    # Process each .md file in Needs_Action
    for task_file in sorted(NEEDS_ACTION_PATH.glob("*.md")):
        if not task_file.is_file():
            continue

        print(f"[PROCESSING] {task_file.name}")

        try:
            # Read task content
            task_content = read_task_content(task_file)

            # Categorize task
            category = categorize_task(task_content)

            # Determine priority
            if is_high_priority(task_content):
                priority = "high"
            elif is_low_priority(task_content):
                priority = "low"
            else:
                priority = "normal"

            # Create execution plan
            plan_name = create_plan(task_file.name, task_content, category, priority)
            print(f"   [+] Plan created: {plan_name}")
            print(f"   [+] Category: {category.replace('_', ' ').title()}")
            print(f"   [+] Priority: {priority.upper()}")

            # Route task based on category
            if category == "auto_complete":
                # Auto-complete and move to Done
                move_task(task_file, DONE_PATH, category)
                print(f"   [OK] AUTO-COMPLETED -> Done/")
                log_action("auto_complete", task_file.name, {
                    "plan": plan_name,
                    "category": category,
                    "priority": priority
                })
                stats["auto_completed"] += 1

            elif category == "approval_required":
                # Move to Pending Approval
                move_task(task_file, PENDING_APPROVAL_PATH, category)
                print(f"   [!] APPROVAL REQUIRED -> Pending_Approval/")
                log_action("requires_approval", task_file.name, {
                    "plan": plan_name,
                    "category": category,
                    "priority": priority
                })
                stats["pending_approval"] += 1

            elif category == "high_priority":
                # Move to High Priority
                move_task(task_file, HIGH_PRIORITY_PATH, category)
                print(f"   [!!] HIGH PRIORITY -> High_Priority/")
                log_action("high_priority", task_file.name, {
                    "plan": plan_name,
                    "category": category,
                    "priority": priority
                })
                stats["high_priority"] += 1

            else:
                # Normal task - stays in Needs_Action for now
                update_task_metadata(task_file, {
                    "category": category,
                    "priority": priority,
                    "processedAt": datetime.now().isoformat()
                })
                print(f"   [*] NORMAL -> Needs_Action/ (awaiting execution)")
                log_action("categorized", task_file.name, {
                    "plan": plan_name,
                    "category": category,
                    "priority": priority
                })
                stats["normal"] += 1

            stats["processed"] += 1
            print()

        except Exception as e:
            print(f"   [X] ERROR: {e}\n")
            log_action("error", task_file.name, {"error": str(e)})

    # Summary
    print("=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total Processed:     {stats['processed']}")
    print(f"[OK] Auto-Completed: {stats['auto_completed']}")
    print(f"[!!] High Priority:  {stats['high_priority']}")
    print(f"[!] Needs Approval:  {stats['pending_approval']}")
    print(f"[*] Normal Tasks:    {stats['normal']}")
    print("=" * 60)


if __name__ == "__main__":
    process_tasks()
