#!/usr/bin/env python3
"""
FastAPI Backend for Personal AI Employee
Provides REST API endpoints for the Next.js frontend.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import shutil
from datetime import datetime

# Import existing modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

app = FastAPI(title="Personal AI Employee API", version="1.0.0")

# CORS middleware for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
VAULT_PATH = Path("../AI_Employee_Vault")
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
HIGH_PRIORITY_PATH = VAULT_PATH / "High_Priority"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
DONE_PATH = VAULT_PATH / "Done"
APPROVED_PATH = VAULT_PATH / "Approved"
REJECTED_PATH = VAULT_PATH / "Rejected"
PLANS_PATH = VAULT_PATH / "Plans"
LOGS_PATH = VAULT_PATH / "Logs"
REPORTS_PATH = VAULT_PATH / "Reports"

# Pydantic models
class Task(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    created_at: str
    processed_at: Optional[str] = None
    folder: str

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "normal"

class TaskAction(BaseModel):
    action: str  # approve, reject, complete

class DashboardStats(BaseModel):
    total_tasks: int
    pending_approval: int
    high_priority: int
    done: int
    inbox: int
    needs_action: int


def parse_task_metadata(file_path: Path) -> Dict[str, Any]:
    """Parse metadata from task file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = {}
        description = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                # Parse metadata
                for line in parts[1].strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                description = parts[2].strip()

        return {
            "metadata": metadata,
            "description": description
        }
    except Exception as e:
        return {
            "metadata": {},
            "description": f"Error reading file: {str(e)}"
        }


def get_task_from_file(file_path: Path, folder: str) -> Task:
    """Convert a task file to a Task object."""
    data = parse_task_metadata(file_path)
    metadata = data["metadata"]
    description = data["description"]

    # Extract title from description (first line)
    title = description.split("\n")[0].replace("#", "").strip()
    if not title:
        title = file_path.stem

    return Task(
        id=file_path.stem,
        title=title,
        description=description,
        status=metadata.get("status", "unknown"),
        priority=metadata.get("priority", "normal"),
        category=metadata.get("category", "normal"),
        created_at=metadata.get("createdAt", ""),
        processed_at=metadata.get("processedAt"),
        folder=folder
    )


def get_all_tasks_from_folder(folder_path: Path, folder_name: str) -> List[Task]:
    """Get all tasks from a folder."""
    tasks = []
    if folder_path.exists():
        for file_path in folder_path.glob("*.md"):
            try:
                task = get_task_from_file(file_path, folder_name)
                tasks.append(task)
            except Exception as e:
                print(f"Error loading task {file_path}: {e}")
    return tasks


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Personal AI Employee API", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/stats", response_model=DashboardStats)
def get_stats():
    """Get dashboard statistics."""
    stats = DashboardStats(
        total_tasks=0,
        pending_approval=len(list(PENDING_APPROVAL_PATH.glob("*.md"))) if PENDING_APPROVAL_PATH.exists() else 0,
        high_priority=len(list(HIGH_PRIORITY_PATH.glob("*.md"))) if HIGH_PRIORITY_PATH.exists() else 0,
        done=len(list(DONE_PATH.glob("*.md"))) if DONE_PATH.exists() else 0,
        inbox=len(list(INBOX_PATH.glob("*.md"))) if INBOX_PATH.exists() else 0,
        needs_action=len(list(NEEDS_ACTION_PATH.glob("*.md"))) if NEEDS_ACTION_PATH.exists() else 0
    )
    stats.total_tasks = (stats.pending_approval + stats.high_priority +
                        stats.done + stats.inbox + stats.needs_action)
    return stats


@app.get("/api/tasks", response_model=List[Task])
def get_tasks(folder: Optional[str] = None, priority: Optional[str] = None):
    """Get all tasks, optionally filtered by folder or priority."""
    all_tasks = []

    folders = {
        "inbox": INBOX_PATH,
        "needs_action": NEEDS_ACTION_PATH,
        "high_priority": HIGH_PRIORITY_PATH,
        "pending_approval": PENDING_APPROVAL_PATH,
        "done": DONE_PATH,
        "approved": APPROVED_PATH,
        "rejected": REJECTED_PATH
    }

    if folder and folder in folders:
        # Get tasks from specific folder
        all_tasks = get_all_tasks_from_folder(folders[folder], folder)
    else:
        # Get tasks from all folders
        for folder_name, folder_path in folders.items():
            tasks = get_all_tasks_from_folder(folder_path, folder_name)
            all_tasks.extend(tasks)

    # Filter by priority if specified
    if priority:
        all_tasks = [t for t in all_tasks if t.priority.lower() == priority.lower()]

    # Sort by created_at (newest first)
    all_tasks.sort(key=lambda x: x.created_at, reverse=True)

    return all_tasks


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    """Get a specific task by ID."""
    # Search all folders
    folders = {
        "inbox": INBOX_PATH,
        "needs_action": NEEDS_ACTION_PATH,
        "high_priority": HIGH_PRIORITY_PATH,
        "pending_approval": PENDING_APPROVAL_PATH,
        "done": DONE_PATH,
        "approved": APPROVED_PATH,
        "rejected": REJECTED_PATH
    }

    for folder_name, folder_path in folders.items():
        file_path = folder_path / f"{task_id}.md"
        if file_path.exists():
            return get_task_from_file(file_path, folder_name)

    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/api/tasks", response_model=Task)
def create_task(task: TaskCreate):
    """Create a new task."""
    # Generate task ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_id = f"task_{timestamp}"

    # Create task content
    content = f"""---
createdAt: {datetime.now().isoformat()}
source: web
status: pending
priority: {task.priority}
---

# {task.title}

{task.description}
"""

    # Save to vault root (will be picked up by watcher)
    file_path = VAULT_PATH / f"{task_id}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Return the created task
    return Task(
        id=task_id,
        title=task.title,
        description=task.description,
        status="pending",
        priority=task.priority,
        category="normal",
        created_at=datetime.now().isoformat(),
        folder="inbox"
    )


@app.post("/api/tasks/{task_id}/action")
def task_action(task_id: str, action: TaskAction):
    """Perform an action on a task (approve, reject, complete)."""
    # Find the task
    task_file = None
    source_folder = None

    folders = {
        "pending_approval": PENDING_APPROVAL_PATH,
        "high_priority": HIGH_PRIORITY_PATH,
        "needs_action": NEEDS_ACTION_PATH,
        "inbox": INBOX_PATH
    }

    for folder_name, folder_path in folders.items():
        file_path = folder_path / f"{task_id}.md"
        if file_path.exists():
            task_file = file_path
            source_folder = folder_name
            break

    if not task_file:
        raise HTTPException(status_code=404, detail="Task not found")

    # Perform action
    if action.action == "approve":
        dest_folder = APPROVED_PATH
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / task_file.name
        shutil.move(str(task_file), str(dest_file))

        # Log action
        log_action("approve", task_id, {"source": source_folder})

        return {"message": "Task approved", "task_id": task_id}

    elif action.action == "reject":
        dest_folder = REJECTED_PATH
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / task_file.name
        shutil.move(str(task_file), str(dest_file))

        # Log action
        log_action("reject", task_id, {"source": source_folder})

        return {"message": "Task rejected", "task_id": task_id}

    elif action.action == "complete":
        dest_folder = DONE_PATH
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / task_file.name
        shutil.move(str(task_file), str(dest_file))

        # Log action
        log_action("complete", task_id, {"source": source_folder})

        return {"message": "Task completed", "task_id": task_id}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")


@app.get("/api/reports/latest")
def get_latest_report():
    """Get the latest CEO briefing report."""
    if not REPORTS_PATH.exists():
        raise HTTPException(status_code=404, detail="No reports found")

    # Find the latest report
    reports = list(REPORTS_PATH.glob("CEO_Briefing_*.md"))
    if not reports:
        raise HTTPException(status_code=404, detail="No reports found")

    latest_report = max(reports, key=lambda p: p.stat().st_mtime)

    # Read and return content
    with open(latest_report, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "filename": latest_report.name,
        "content": content,
        "generated_at": datetime.fromtimestamp(latest_report.stat().st_mtime).isoformat()
    }


@app.post("/api/reports/generate")
def generate_report():
    """Trigger CEO briefing generation."""
    import subprocess

    try:
        result = subprocess.run(
            ["python", "scripts/generate_briefing.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            return {"message": "Report generated successfully", "output": result.stdout}
        else:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {result.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@app.get("/api/logs/today")
def get_today_logs():
    """Get today's activity logs."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    if not log_file.exists():
        return {"date": today, "logs": []}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
        return {"date": today, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")


def log_action(action_type: str, task_id: str, details: Dict = None):
    """Log an action to today's log file."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,
        "file": task_id,
        "source": "web"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
