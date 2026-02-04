#!/usr/bin/env python3
"""
Runner Script for AI Employee System
Processes tasks in Needs_Action folder and creates execution plans.
"""

import os
import json
from datetime import datetime
from pathlib import Path


VAULT_PATH = Path("./AI_Employee_Vault")
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
PLANS_PATH = VAULT_PATH / "Plans"
LOGS_PATH = VAULT_PATH / "Logs"

# Keywords that require human approval
APPROVAL_KEYWORDS = [
    "email", "message", "whatsapp", "contact",
    "payment", "money", "bank", "transfer",
    "send", "reply", "respond"
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


def requires_approval(task_content):
    """Check if task content contains keywords requiring approval."""
    content_lower = task_content.lower()
    return any(keyword in content_lower for keyword in APPROVAL_KEYWORDS)


def create_plan(task_name, task_content, requires_human_approval):
    """Create a plan file with checkbox steps."""
    plan_name = Path(task_name).stem + "_plan.md"
    plan_path = PLANS_PATH / plan_name

    timestamp = datetime.now().isoformat()

    # Generate plan steps based on task content
    steps = [
        "- [ ] Analyze task requirements",
        "- [ ] Gather necessary information",
        "- [ ] Break down task into subtasks",
        "- [ ] Execute primary actions",
        "- [ ] Verify results",
        "- [ ] Document outcomes",
        "- [ ] Update task status",
        "- [ ] Archive completed work"
    ]

    plan_content = f"""---
taskFile: {task_name}
createdAt: {timestamp}
requiresApproval: {requires_human_approval}
status: pending
---

# Execution Plan: {Path(task_name).stem}

## Task Summary
{task_content[:200]}{'...' if len(task_content) > 200 else ''}

## Execution Steps
{chr(10).join(steps)}

## Notes
- This plan was automatically generated
{'- **⚠️ REQUIRES HUMAN APPROVAL before execution**' if requires_human_approval else '- Can be executed automatically'}

## Execution Log
_Will be populated during execution_
"""

    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(plan_content)

    return plan_name


def move_to_pending_approval(file_path):
    """Move task file to Pending_Approval folder."""
    dest = PENDING_APPROVAL_PATH / file_path.name
    file_path.rename(dest)
    return dest


def process_tasks():
    """Process all tasks in Needs_Action folder."""
    # Ensure directories exist
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
    PENDING_APPROVAL_PATH.mkdir(parents=True, exist_ok=True)
    PLANS_PATH.mkdir(parents=True, exist_ok=True)
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    processed = 0
    requires_approval_count = 0

    print("Starting Task Runner...")
    print(f"Processing tasks in: {NEEDS_ACTION_PATH.absolute()}\n")

    # Process each .md file in Needs_Action
    for task_file in NEEDS_ACTION_PATH.glob("*.md"):
        if not task_file.is_file():
            continue

        print(f"Processing: {task_file.name}")

        try:
            # Read task content
            task_content = read_task_content(task_file)

            # Check if requires approval
            needs_approval = requires_approval(task_content)

            # Create execution plan
            plan_name = create_plan(task_file.name, task_content, needs_approval)
            print(f"  ✓ Created plan: {plan_name}")

            # Move to Pending_Approval if needed
            if needs_approval:
                move_to_pending_approval(task_file)
                print(f"  ⚠️  Moved to Pending_Approval (requires human approval)")
                log_action("create_plan_approval_required", task_file.name, {
                    "plan": plan_name,
                    "reason": "contains approval keywords"
                })
                requires_approval_count += 1
            else:
                log_action("create_plan", task_file.name, {"plan": plan_name})

            processed += 1
            print()

        except Exception as e:
            print(f"  ✗ Error processing {task_file.name}: {e}\n")
            log_action("error", task_file.name, {"error": str(e)})

    # Summary
    print("=" * 50)
    print(f"Tasks processed: {processed}")
    print(f"Requires approval: {requires_approval_count}")
    print(f"Can auto-execute: {processed - requires_approval_count}")
    print("=" * 50)


if __name__ == "__main__":
    process_tasks()
