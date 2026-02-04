#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silver Tier AI Employee - Main Launcher
Provides menu-driven interface for all Silver Tier features.
"""

import subprocess
import sys
from pathlib import Path

# Ensure proper encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCRIPTS = {
    "1": {
        "name": "Start Silver Tier Watcher",
        "script": "watchers/inbox_watcher_silver.py",
        "description": "Monitor inbox and auto-process tasks with intelligent routing"
    },
    "2": {
        "name": "Run Silver Tier Task Processor",
        "script": "scripts/runner_silver.py",
        "description": "Process tasks with priority categorization and auto-completion"
    },
    "3": {
        "name": "Generate CEO Weekly Briefing",
        "script": "scripts/generate_briefing.py",
        "description": "Create executive summary report of task activity"
    },
    "4": {
        "name": "Start Bronze Watcher (Basic)",
        "script": "watchers/inbox_watcher.py",
        "description": "Original inbox watcher without auto-processing"
    },
    "5": {
        "name": "Run Bronze Task Processor (Basic)",
        "script": "scripts/runner.py",
        "description": "Original task processor without Silver features"
    }
}


def print_banner():
    """Print application banner."""
    print("\n" + "=" * 60)
    print("PERSONAL AI EMPLOYEE - SILVER TIER MVP")
    print("=" * 60)
    print("Hackathon 0 Submission - Intelligent Task Management System")
    print("=" * 60 + "\n")


def print_menu():
    """Print main menu."""
    print("Available Options:\n")
    for key, info in SCRIPTS.items():
        print(f"  [{key}] {info['name']}")
        print(f"      {info['description']}\n")
    print("  [q] Quit\n")


def run_script(script_path):
    """Run a Python script."""
    script = Path(script_path)

    if not script.exists():
        print(f"\n[ERROR] Script not found: {script_path}")
        input("\nPress Enter to continue...")
        return

    print(f"\n{'=' * 60}")
    print(f"Launching: {script.name}")
    print(f"{'=' * 60}\n")

    try:
        subprocess.run([sys.executable, str(script)])
    except KeyboardInterrupt:
        print("\n\n[!] Script interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error running script: {e}")

    input("\nPress Enter to continue...")


def show_status():
    """Show system status."""
    from pathlib import Path

    vault = Path("./AI_Employee_Vault")
    folders = {
        "Inbox": vault / "Inbox",
        "Needs_Action": vault / "Needs_Action",
        "High_Priority": vault / "High_Priority",
        "Pending_Approval": vault / "Pending_Approval",
        "Done": vault / "Done",
        "Approved": vault / "Approved",
        "Rejected": vault / "Rejected"
    }

    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60 + "\n")

    total_tasks = 0
    for name, path in folders.items():
        if path.exists():
            count = len(list(path.glob("*.md")))
            total_tasks += count
            status_icon = "[!]" if count > 0 else "   "
            print(f"{status_icon} {name:20} : {count:3} tasks")
        else:
            print(f"    {name:20} : --- (not found)")

    print("\n" + "-" * 60)
    print(f"Total Tasks in System: {total_tasks}")
    print("=" * 60 + "\n")


def main():
    """Main application loop."""
    while True:
        print_banner()
        show_status()
        print_menu()

        choice = input("Select an option: ").strip().lower()

        if choice == 'q':
            print("\nGoodbye!\n")
            break
        elif choice in SCRIPTS:
            run_script(SCRIPTS[choice]["script"])
        else:
            print("\n[ERROR] Invalid option. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n")
        sys.exit(0)
