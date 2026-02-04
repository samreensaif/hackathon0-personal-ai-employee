#!/usr/bin/env python3
"""
Silver Tier Test Script
Creates sample tasks to demonstrate all categorization features.
"""

from pathlib import Path
from datetime import datetime


VAULT_PATH = Path("./AI_Employee_Vault")


def create_test_task(filename, content):
    """Create a test task file in vault root."""
    task_path = VAULT_PATH / filename

    with open(task_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Created test task: {filename}")


def create_test_tasks():
    """Create a suite of test tasks demonstrating all categories."""

    print("=" * 60)
    print("SILVER TIER - Test Task Generator")
    print("=" * 60)
    print("Creating sample tasks to demonstrate categorization...\n")

    # 1. Auto-Complete Task (Low Priority, Simple)
    create_test_task("test_reminder.md", """# Reminder Task

FYI - Remember to review the monthly report when it's ready.

This is just a simple reminder note for later reference.
""")

    # 2. High Priority Task
    create_test_task("test_urgent.md", """# URGENT: Server Issue

CRITICAL: Production server showing high CPU usage.

Deadline: Today - needs immediate attention!

Please investigate ASAP and report findings.
""")

    # 3. Approval Required Task (Email)
    create_test_task("test_email.md", """# Client Email Response

Need to send an email to client regarding project status update.

Draft response:
- Confirm milestone completion
- Discuss next steps
- Schedule follow-up meeting

Please approve before sending.
""")

    # 4. Approval Required Task (Payment)
    create_test_task("test_payment.md", """# Vendor Payment Request

Process payment for Invoice #12345

Vendor: ABC Services Inc.
Amount: $2,500.00
Due Date: February 15, 2026

Requires approval before bank transfer.
""")

    # 5. Normal Priority Task
    create_test_task("test_normal.md", """# Update Documentation

Update the user guide with new feature descriptions.

Tasks:
- Add screenshots
- Update feature list
- Review for accuracy
- Publish to website

Standard priority - complete this week.
""")

    # 6. Low Priority Info
    create_test_task("test_info.md", """# Information Note

This is just for your information - read when you have time.

The new company handbook is available in the shared drive.

No action needed, just a heads up.
""")

    # 7. Multiple Keywords (Priority Wins)
    create_test_task("test_mixed.md", """# Important Email

URGENT: Need to send critical email to stakeholders today.

This is both important and requires approval for sending.

Deadline: End of day.
""")

    print("\n" + "=" * 60)
    print("[SUCCESS] Test tasks created successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python watchers/inbox_watcher_silver.py")
    print("   (Wait 6-9 seconds for auto-processing)")
    print("   OR")
    print("2. Run manually:")
    print("   - python scripts/runner_silver.py")
    print("\n3. Check the results:")
    print("   - Auto-complete -> Done/")
    print("   - High priority -> High_Priority/")
    print("   - Approval needed -> Pending_Approval/")
    print("   - Normal tasks -> Needs_Action/")
    print("\n4. Generate briefing:")
    print("   - python scripts/generate_briefing.py")
    print("=" * 60)


if __name__ == "__main__":
    # Ensure vault exists
    if not VAULT_PATH.exists():
        print(f"[ERROR] Vault not found at {VAULT_PATH.absolute()}")
        print("Please ensure AI_Employee_Vault directory exists.")
        exit(1)

    create_test_tasks()
