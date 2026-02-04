# Personal AI Employee - Bronze MVP

Hackathon 0 submission for automated task management system.

## Structure

```
AI_Employee_Vault/
├── Inbox/              # Staging area for new tasks
├── Needs_Action/       # Tasks ready for processing
├── Pending_Approval/   # Tasks requiring human approval
├── Approved/           # Approved tasks ready for execution
├── Rejected/           # Rejected tasks
├── Done/               # Completed tasks
├── Plans/              # Execution plans
├── Logs/               # Daily JSON logs
├── Dashboard.md        # System overview
├── Company_Handbook.md # Guidelines
└── Welcome.md          # Introduction

watchers/
└── inbox_watcher.py    # Monitors and moves task files

scripts/
└── runner.py           # Creates execution plans for tasks
```

## Usage

### 1. Start the Inbox Watcher

The watcher monitors for new task files and automatically processes them:

```bash
python watchers/inbox_watcher.py
```

This will:
- Poll every 3 seconds
- Move any `.md` file from vault root → Inbox (except Dashboard.md, Company_Handbook.md, Welcome.md)
- Move files from Inbox → Needs_Action with metadata

### 2. Process Tasks with Runner

Run the task processor to create execution plans:

```bash
python scripts/runner.py
```

This will:
- Process all `.md` files in `Needs_Action/`
- Create execution plans in `Plans/` folder
- Move tasks containing sensitive keywords (email, payment, etc.) to `Pending_Approval/`
- Log all actions to `Logs/YYYY-MM-DD.json`

## Workflow

1. Drop a task file (`.md`) into the vault root or Inbox folder
2. Inbox watcher automatically moves it to `Needs_Action/` with metadata
3. Run `runner.py` to create execution plan
4. Tasks with sensitive keywords go to `Pending_Approval/`
5. Review and approve/reject as needed

## Logs

All actions are logged to daily JSON files in `Logs/YYYY-MM-DD.json`:

```json
[
  {
    "timestamp": "2026-02-04T20:00:00",
    "action": "move_to_inbox",
    "file": "task1.md",
    "source": "root",
    "destination": "Inbox"
  }
]
```

## Requirements

- Python 3.6+ (standard library only)
- No external dependencies

## Keywords Requiring Approval

Tasks containing these keywords require human approval:
- email, message, whatsapp, contact
- payment, money, bank, transfer
- send, reply, respond
