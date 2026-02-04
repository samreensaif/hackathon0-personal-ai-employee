#!/usr/bin/env python3
"""
Silver Tier Inbox Watcher for AI Employee System
Enhanced with automatic runner integration and smart processing.
"""

import os
import time
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


VAULT_PATH = Path("./AI_Employee_Vault")
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"

EXCLUDED_FILES = {"Dashboard.md", "Company_Handbook.md", "Welcome.md"}
POLL_INTERVAL = 3  # seconds
AUTO_PROCESS = True  # Automatically run runner when tasks arrive


def log_action(action_type, file_name, source, destination):
    """Log action to daily JSON log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,
        "file": file_name,
        "source": source,
        "destination": destination
    }

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


def move_from_root_to_inbox():
    """Move .md files from vault root to Inbox (excluding special files)."""
    moved = 0

    if not VAULT_PATH.exists():
        return moved

    for file_path in VAULT_PATH.glob("*.md"):
        if file_path.name in EXCLUDED_FILES:
            continue

        if file_path.is_file():
            dest = INBOX_PATH / file_path.name
            shutil.move(str(file_path), str(dest))
            log_action("move_to_inbox", file_path.name, "root", "Inbox")
            moved += 1
            print(f"📥 Moved {file_path.name} to Inbox/")

    return moved


def prepend_metadata(file_path):
    """Prepend metadata to the file content."""
    timestamp = datetime.now().isoformat()
    metadata = f"""---
createdAt: {timestamp}
source: inbox
status: pending
---

"""

    # Read existing content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if metadata already exists
    if content.startswith("---"):
        return False

    # Write metadata + content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(metadata + content)

    return True


def move_from_inbox_to_needs_action():
    """Move .md files from Inbox to Needs_Action with metadata."""
    moved = 0

    if not INBOX_PATH.exists():
        return moved

    for file_path in INBOX_PATH.glob("*.md"):
        if file_path.is_file():
            dest = NEEDS_ACTION_PATH / file_path.name

            # First move the file
            shutil.move(str(file_path), str(dest))

            # Then add metadata
            prepend_metadata(dest)

            log_action("move_to_needs_action", file_path.name, "Inbox", "Needs_Action")
            moved += 1
            print(f"✅ Moved {file_path.name} to Needs_Action/ with metadata")

    return moved


def run_silver_runner():
    """Execute the Silver Tier runner script to process tasks."""
    runner_script = Path("scripts/runner_silver.py")

    if not runner_script.exists():
        print("⚠️  Silver runner not found, skipping auto-processing")
        return False

    try:
        print("\n🚀 Auto-processing tasks with Silver Tier Runner...")
        print("-" * 60)

        result = subprocess.run(
            ["python", str(runner_script)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(result.stdout)
            print("-" * 60)
            print("✅ Auto-processing completed\n")
            return True
        else:
            print(f"⚠️  Runner error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⚠️  Runner timeout - tasks may still be processing")
        return False
    except Exception as e:
        print(f"⚠️  Runner exception: {e}")
        return False


def watch_inbox():
    """Main watcher loop with Silver Tier features."""
    print("=" * 60)
    print("🚀 SILVER TIER AI EMPLOYEE - Inbox Watcher")
    print("=" * 60)
    print(f"Vault path: {VAULT_PATH.absolute()}")
    print(f"Polling interval: {POLL_INTERVAL} seconds")
    print(f"Auto-processing: {'ENABLED' if AUTO_PROCESS else 'DISABLED'}")
    print("Press Ctrl+C to stop\n")

    # Ensure directories exist
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    cycle_count = 0

    try:
        while True:
            cycle_count += 1

            # Step 1: Move from root to Inbox
            root_moved = move_from_root_to_inbox()

            # Step 2: Move from Inbox to Needs_Action
            inbox_moved = move_from_inbox_to_needs_action()

            # Step 3: Auto-process if tasks were moved
            if AUTO_PROCESS and inbox_moved > 0:
                run_silver_runner()

            if root_moved > 0 or inbox_moved > 0:
                print(f"📊 Cycle {cycle_count}: {root_moved} from root, {inbox_moved} from Inbox\n")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Stopping Silver Tier Inbox Watcher...")
        print(f"Total cycles completed: {cycle_count}")
        print("=" * 60)


if __name__ == "__main__":
    watch_inbox()
