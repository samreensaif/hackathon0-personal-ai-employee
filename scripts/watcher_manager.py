#!/usr/bin/env python3
"""
Watcher Manager for AI Employee System

Manages all watchers as background processes with health monitoring,
centralized logging, and a real-time status dashboard.

Features:
- Start/stop all watchers with one command
- Monitor health and auto-restart on crashes
- Aggregate logs from all watchers
- Real-time terminal dashboard
- Graceful shutdown (Ctrl+C)
- Configuration file for enabling/disabling watchers
- Process isolation with multiprocessing

Usage:
    python scripts/watcher_manager.py                  # Start all enabled watchers
    python scripts/watcher_manager.py --status         # Show status only
    python scripts/watcher_manager.py --stop           # Stop all watchers
    python scripts/watcher_manager.py --config         # Show configuration

Version: 1.0.0
Author: AI Employee System
"""

import os
import sys
import time
import json
import signal
import argparse
import subprocess
import multiprocessing as mp
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from queue import Queue, Empty
from threading import Thread

# Try to import rich for beautiful terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[WARNING] 'rich' not installed. Using basic output.")
    print("Install with: pip install rich")


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "AI_Employee_Vault"
LOGS_PATH = VAULT_PATH / "Logs"
CONFIG_FILE = PROJECT_ROOT / "config" / "watcher_config.json"
PID_FILE = PROJECT_ROOT / ".watcher_manager.pid"

# Default configuration
DEFAULT_CONFIG = {
    "watchers": {
        "inbox_watcher": {
            "enabled": True,
            "script": "watchers/inbox_watcher_silver.py",
            "description": "Monitors filesystem inbox",
            "restart_on_crash": True,
            "max_restarts": 5,
            "restart_delay": 10,
            "health_check_interval": 30
        },
        "gmail_watcher": {
            "enabled": True,
            "script": "watchers/gmail_watcher.py",
            "description": "Monitors Gmail inbox",
            "restart_on_crash": True,
            "max_restarts": 5,
            "restart_delay": 10,
            "health_check_interval": 30
        },
        "linkedin_watcher": {
            "enabled": False,
            "script": "watchers/linkedin_watcher.py",
            "description": "Monitors LinkedIn notifications",
            "restart_on_crash": True,
            "max_restarts": 5,
            "restart_delay": 10,
            "health_check_interval": 30
        }
    },
    "manager": {
        "log_aggregation": True,
        "status_update_interval": 2,
        "max_log_lines": 100,
        "dashboard_refresh_rate": 1.0
    }
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class WatcherStatus:
    """Status information for a watcher process."""
    name: str
    pid: Optional[int] = None
    status: str = "stopped"  # stopped, starting, running, crashed, stopping
    uptime: float = 0.0
    restarts: int = 0
    last_restart: Optional[datetime] = None
    last_error: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    processed_count: int = 0
    error_count: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        if self.last_restart:
            data['last_restart'] = self.last_restart.isoformat()
        if self.last_heartbeat:
            data['last_heartbeat'] = self.last_heartbeat.isoformat()
        return data


# ============================================================================
# WATCHER PROCESS WRAPPER
# ============================================================================

class WatcherProcess:
    """Wrapper for a watcher process with health monitoring."""

    def __init__(self, name: str, config: Dict, log_queue: mp.Queue):
        """
        Initialize watcher process.

        Args:
            name: Watcher name
            config: Watcher configuration
            log_queue: Queue for aggregated logging
        """
        self.name = name
        self.config = config
        self.log_queue = log_queue
        self.process: Optional[mp.Process] = None
        self.status = WatcherStatus(name=name)
        self.start_time: Optional[datetime] = None
        self.should_stop = mp.Event()

    def start(self) -> bool:
        """
        Start the watcher process.

        Returns:
            True if started successfully, False otherwise
        """
        if self.process and self.process.is_alive():
            self.log("warning", "Already running")
            return False

        script_path = PROJECT_ROOT / self.config['script']
        if not script_path.exists():
            self.log("error", f"Script not found: {script_path}")
            self.status.status = "crashed"
            self.status.last_error = f"Script not found: {script_path}"
            return False

        try:
            self.status.status = "starting"
            self.start_time = datetime.now()

            # Create process
            self.process = mp.Process(
                target=self._run_watcher,
                args=(script_path,),
                name=f"watcher_{self.name}",
                daemon=True
            )

            self.process.start()
            self.status.pid = self.process.pid
            self.status.status = "running"
            self.status.last_heartbeat = datetime.now()

            self.log("info", f"Started with PID {self.process.pid}")
            return True

        except Exception as e:
            self.log("error", f"Failed to start: {e}")
            self.status.status = "crashed"
            self.status.last_error = str(e)
            return False

    def _run_watcher(self, script_path: Path):
        """
        Run the watcher script as a subprocess.

        Args:
            script_path: Path to watcher script
        """
        try:
            # Run the watcher script
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=str(PROJECT_ROOT)
            )

            # Monitor output
            while not self.should_stop.is_set():
                # Check if process ended
                if process.poll() is not None:
                    break

                # Read stdout
                line = process.stdout.readline()
                if line:
                    self.log("info", line.strip())
                    self.status.last_heartbeat = datetime.now()

                # Check stderr
                try:
                    # Non-blocking read
                    import select
                    if select.select([process.stderr], [], [], 0)[0]:
                        err_line = process.stderr.readline()
                        if err_line:
                            self.log("error", err_line.strip())
                            self.status.error_count += 1
                except:
                    pass

                time.sleep(0.1)

            # Process ended or stopped
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)

        except Exception as e:
            self.log("error", f"Watcher crashed: {e}")
            self.status.last_error = str(e)

    def stop(self, timeout: int = 10) -> bool:
        """
        Stop the watcher process gracefully.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.process or not self.process.is_alive():
            self.status.status = "stopped"
            return True

        try:
            self.status.status = "stopping"
            self.should_stop.set()

            self.log("info", "Stopping...")

            # Wait for graceful shutdown
            self.process.join(timeout=timeout)

            if self.process.is_alive():
                # Force terminate
                self.log("warning", "Forcing termination...")
                self.process.terminate()
                self.process.join(timeout=5)

                if self.process.is_alive():
                    # Force kill
                    self.process.kill()
                    self.process.join(timeout=2)

            self.status.status = "stopped"
            self.status.pid = None
            self.log("info", "Stopped")
            return True

        except Exception as e:
            self.log("error", f"Failed to stop: {e}")
            return False

    def is_alive(self) -> bool:
        """Check if watcher process is alive."""
        return self.process is not None and self.process.is_alive()

    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        if not self.start_time or not self.is_alive():
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()

    def needs_restart(self) -> bool:
        """Check if watcher needs to be restarted."""
        if not self.config.get('restart_on_crash', True):
            return False

        if self.status.status == "crashed":
            return True

        if not self.is_alive() and self.status.status == "running":
            return True

        # Check for stale heartbeat
        if self.status.last_heartbeat:
            age = (datetime.now() - self.status.last_heartbeat).total_seconds()
            if age > self.config.get('health_check_interval', 30) * 3:
                self.log("warning", "Heartbeat timeout - may be stuck")
                return True

        return False

    def can_restart(self) -> bool:
        """Check if watcher can be restarted."""
        max_restarts = self.config.get('max_restarts', 5)
        if self.status.restarts >= max_restarts:
            self.log("error", f"Max restarts ({max_restarts}) reached")
            return False

        if self.status.last_restart:
            delay = self.config.get('restart_delay', 10)
            age = (datetime.now() - self.status.last_restart).total_seconds()
            if age < delay:
                return False

        return True

    def restart(self) -> bool:
        """Restart the watcher process."""
        self.log("info", "Restarting...")

        # Stop first
        self.stop(timeout=5)

        # Wait a bit
        time.sleep(2)

        # Start again
        if self.start():
            self.status.restarts += 1
            self.status.last_restart = datetime.now()
            return True

        return False

    def log(self, level: str, message: str):
        """
        Send log message to aggregated log queue.

        Args:
            level: Log level (info, warning, error)
            message: Log message
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "watcher": self.name,
                "level": level,
                "message": message
            }
            self.log_queue.put_nowait(log_entry)
        except:
            pass  # Queue full or closed

    def update_status(self):
        """Update status information."""
        if self.is_alive():
            self.status.status = "running"
            self.status.uptime = self.get_uptime()
        elif self.status.status == "running":
            self.status.status = "crashed"
            self.status.last_error = "Process died unexpectedly"


# ============================================================================
# WATCHER MANAGER
# ============================================================================

class WatcherManager:
    """Manages all watcher processes."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize watcher manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or CONFIG_FILE
        self.config = self.load_config()
        self.watchers: Dict[str, WatcherProcess] = {}
        self.log_queue = mp.Queue(maxsize=1000)
        self.log_buffer: List[Dict] = []
        self.running = False
        self.console = Console() if RICH_AVAILABLE else None

        # Ensure directories exist
        LOGS_PATH.mkdir(parents=True, exist_ok=True)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return config
            except Exception as e:
                print(f"[WARNING] Failed to load config: {e}")
                print("[INFO] Using default configuration")

        # Create default config
        self.save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    def save_config(self, config: Optional[Dict] = None):
        """Save configuration to file."""
        config = config or self.config

        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")

    def initialize_watchers(self):
        """Initialize all enabled watchers."""
        watcher_configs = self.config.get('watchers', {})

        for name, wconfig in watcher_configs.items():
            if not wconfig.get('enabled', False):
                continue

            watcher = WatcherProcess(name, wconfig, self.log_queue)
            self.watchers[name] = watcher

    def start_all(self) -> int:
        """
        Start all enabled watchers.

        Returns:
            Number of watchers started successfully
        """
        self.initialize_watchers()

        if not self.watchers:
            print("[WARNING] No watchers enabled")
            return 0

        started = 0
        for name, watcher in self.watchers.items():
            print(f"[INFO] Starting {name}...")
            if watcher.start():
                started += 1
            else:
                print(f"[ERROR] Failed to start {name}")

        return started

    def stop_all(self, timeout: int = 10) -> int:
        """
        Stop all running watchers.

        Args:
            timeout: Timeout in seconds per watcher

        Returns:
            Number of watchers stopped successfully
        """
        stopped = 0

        for name, watcher in self.watchers.items():
            if watcher.is_alive():
                print(f"[INFO] Stopping {name}...")
                if watcher.stop(timeout=timeout):
                    stopped += 1

        return stopped

    def monitor_health(self):
        """Monitor health of all watchers and restart if needed."""
        for name, watcher in self.watchers.items():
            watcher.update_status()

            if watcher.needs_restart():
                if watcher.can_restart():
                    print(f"\n[WARNING] {name} needs restart - restarting...")
                    watcher.restart()
                else:
                    print(f"\n[ERROR] {name} cannot be restarted (max restarts reached)")

    def process_logs(self):
        """Process logs from queue into buffer."""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                self.log_buffer.append(log_entry)

                # Keep buffer size limited
                max_lines = self.config['manager'].get('max_log_lines', 100)
                if len(self.log_buffer) > max_lines:
                    self.log_buffer.pop(0)

                # Also write to daily log file
                self.write_log_to_file(log_entry)

        except Empty:
            pass

    def write_log_to_file(self, log_entry: Dict):
        """Write log entry to daily log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS_PATH / f"{today}.json"

        # Read existing logs
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []

        # Append new log
        logs.append(log_entry)

        # Write back
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Failed to write log: {e}")

    def get_status_summary(self) -> Dict:
        """Get summary of all watcher statuses."""
        summary = {
            "total": len(self.watchers),
            "running": 0,
            "stopped": 0,
            "crashed": 0,
            "total_restarts": 0,
            "total_errors": 0
        }

        for watcher in self.watchers.values():
            if watcher.status.status == "running":
                summary["running"] += 1
            elif watcher.status.status == "stopped":
                summary["stopped"] += 1
            elif watcher.status.status == "crashed":
                summary["crashed"] += 1

            summary["total_restarts"] += watcher.status.restarts
            summary["total_errors"] += watcher.status.error_count

        return summary

    def create_dashboard(self) -> Table:
        """Create rich dashboard table."""
        if not RICH_AVAILABLE:
            return None

        table = Table(
            title="[bold cyan]Watcher Manager Dashboard[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )

        table.add_column("Watcher", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("PID", justify="right", style="yellow")
        table.add_column("Uptime", justify="right", style="green")
        table.add_column("Restarts", justify="center", style="blue")
        table.add_column("Errors", justify="center", style="red")
        table.add_column("Last Heartbeat", style="dim")

        for name, watcher in sorted(self.watchers.items()):
            status = watcher.status

            # Status with color
            if status.status == "running":
                status_text = "[green]●[/green] Running"
            elif status.status == "stopped":
                status_text = "[dim]○[/dim] Stopped"
            elif status.status == "crashed":
                status_text = "[red]✗[/red] Crashed"
            elif status.status == "starting":
                status_text = "[yellow]◐[/yellow] Starting"
            else:
                status_text = f"[dim]{status.status}[/dim]"

            # Uptime
            uptime_seconds = watcher.get_uptime()
            if uptime_seconds > 0:
                uptime_str = self.format_duration(uptime_seconds)
            else:
                uptime_str = "-"

            # PID
            pid_str = str(status.pid) if status.pid else "-"

            # Heartbeat
            if status.last_heartbeat:
                hb_age = (datetime.now() - status.last_heartbeat).total_seconds()
                if hb_age < 10:
                    hb_str = "Just now"
                elif hb_age < 60:
                    hb_str = f"{int(hb_age)}s ago"
                else:
                    hb_str = f"{int(hb_age/60)}m ago"
            else:
                hb_str = "-"

            table.add_row(
                name,
                status_text,
                pid_str,
                uptime_str,
                str(status.restarts),
                str(status.error_count),
                hb_str
            )

        return table

    def create_log_panel(self) -> Panel:
        """Create log panel showing recent logs."""
        if not RICH_AVAILABLE:
            return None

        # Get last N log entries
        recent_logs = self.log_buffer[-20:]

        log_lines = []
        for log in recent_logs:
            timestamp = log['timestamp'][11:19]  # HH:MM:SS
            watcher = log['watcher'][:15].ljust(15)
            level = log['level'].upper()
            message = log['message'][:60]

            # Color by level
            if level == "ERROR":
                line = f"[red]{timestamp}[/red] [{watcher}] [bold red]{level:7}[/bold red] {message}"
            elif level == "WARNING":
                line = f"[yellow]{timestamp}[/yellow] [{watcher}] [bold yellow]{level:7}[/bold yellow] {message}"
            else:
                line = f"[dim]{timestamp}[/dim] [{watcher}] [blue]{level:7}[/blue] {message}"

            log_lines.append(line)

        log_text = "\n".join(log_lines) if log_lines else "[dim]No recent logs[/dim]"

        return Panel(
            log_text,
            title="[bold]Recent Logs[/bold]",
            border_style="blue"
        )

    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m {int(seconds%60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def run_dashboard(self):
        """Run live dashboard."""
        if not RICH_AVAILABLE:
            print("[WARNING] Rich not available. Using basic monitoring.")
            self.run_basic_monitoring()
            return

        try:
            with Live(
                self.create_dashboard(),
                refresh_per_second=self.config['manager'].get('dashboard_refresh_rate', 1.0),
                console=self.console
            ) as live:
                while self.running:
                    # Process logs
                    self.process_logs()

                    # Monitor health
                    self.monitor_health()

                    # Update dashboard
                    layout = Layout()
                    layout.split_column(
                        Layout(self.create_dashboard(), size=len(self.watchers) + 5),
                        Layout(self.create_log_panel())
                    )
                    live.update(layout)

                    time.sleep(self.config['manager'].get('status_update_interval', 2))

        except KeyboardInterrupt:
            pass

    def run_basic_monitoring(self):
        """Run basic monitoring without rich."""
        print("\n" + "=" * 70)
        print("Watcher Manager - Basic Monitoring Mode")
        print("=" * 70)
        print("Press Ctrl+C to stop\n")

        try:
            while self.running:
                # Process logs
                self.process_logs()

                # Monitor health
                self.monitor_health()

                # Print status
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n" + "=" * 70)
                print(f"Watcher Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70)

                for name, watcher in sorted(self.watchers.items()):
                    status = watcher.status
                    uptime = self.format_duration(watcher.get_uptime())
                    print(f"\n[{name}]")
                    print(f"  Status: {status.status}")
                    print(f"  PID: {status.pid if status.pid else '-'}")
                    print(f"  Uptime: {uptime}")
                    print(f"  Restarts: {status.restarts}")
                    print(f"  Errors: {status.error_count}")

                print("\n" + "=" * 70)
                print("Recent logs:")
                print("-" * 70)

                for log in self.log_buffer[-10:]:
                    timestamp = log['timestamp'][11:19]
                    print(f"{timestamp} [{log['watcher']}] {log['level'].upper()}: {log['message'][:50]}")

                print("\n")

                time.sleep(self.config['manager'].get('status_update_interval', 2))

        except KeyboardInterrupt:
            pass

    def run(self):
        """Run watcher manager with dashboard."""
        self.running = True

        # Write PID file
        try:
            with open(PID_FILE, 'w') as f:
                f.write(str(os.getpid()))
        except:
            pass

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start all watchers
        started = self.start_all()

        if started == 0:
            print("[ERROR] No watchers started")
            return 1

        print(f"\n[SUCCESS] Started {started} watcher(s)")
        print("[INFO] Starting dashboard...\n")

        time.sleep(2)

        # Run dashboard
        self.run_dashboard()

        # Cleanup
        self.cleanup()

        return 0

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n\n[INFO] Received shutdown signal")
        self.running = False

    def cleanup(self):
        """Cleanup on shutdown."""
        print("\n[INFO] Shutting down...")

        # Stop all watchers
        stopped = self.stop_all(timeout=10)
        print(f"[INFO] Stopped {stopped} watcher(s)")

        # Remove PID file
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
        except:
            pass

        print("[INFO] Goodbye!")


# ============================================================================
# CLI
# ============================================================================

def show_status():
    """Show status of running watchers."""
    print("\nWatcher Status")
    print("=" * 70)

    if not PID_FILE.exists():
        print("Watcher manager is not running")
        return

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Check if process is running
        try:
            os.kill(pid, 0)
            print(f"Watcher manager is running (PID: {pid})")
        except OSError:
            print("Watcher manager PID file exists but process is not running")
            PID_FILE.unlink()

    except Exception as e:
        print(f"Error checking status: {e}")


def show_config():
    """Show current configuration."""
    manager = WatcherManager()

    print("\nWatcher Configuration")
    print("=" * 70)
    print(json.dumps(manager.config, indent=2))


def stop_manager():
    """Stop running watcher manager."""
    if not PID_FILE.exists():
        print("[INFO] Watcher manager is not running")
        return

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        print(f"[INFO] Stopping watcher manager (PID: {pid})...")

        # Send SIGTERM
        os.kill(pid, signal.SIGTERM)

        # Wait for shutdown
        for i in range(30):
            time.sleep(1)
            try:
                os.kill(pid, 0)
            except OSError:
                print("[SUCCESS] Watcher manager stopped")
                return

        # Force kill if still running
        print("[WARNING] Forcing shutdown...")
        os.kill(pid, signal.SIGKILL)
        print("[SUCCESS] Watcher manager stopped (forced)")

    except Exception as e:
        print(f"[ERROR] Failed to stop: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Watcher Manager for AI Employee System"
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show status of running watchers'
    )
    parser.add_argument(
        '--stop',
        action='store_true',
        help='Stop all running watchers'
    )
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show current configuration'
    )

    args = parser.parse_args()

    # Handle commands
    if args.status:
        show_status()
        return 0

    if args.stop:
        stop_manager()
        return 0

    if args.config:
        show_config()
        return 0

    # Start manager
    manager = WatcherManager()
    return manager.run()


if __name__ == "__main__":
    sys.exit(main())
