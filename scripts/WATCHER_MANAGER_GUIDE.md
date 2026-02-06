# Watcher Manager Guide

Complete guide for managing all watchers with a single command and real-time dashboard.

---

## 📋 Overview

The Watcher Manager is a production-ready process manager that:

- ✅ Starts/stops all watchers with one command
- ✅ Monitors health and auto-restarts on crashes
- ✅ Aggregates logs from all watchers
- ✅ Displays real-time terminal dashboard
- ✅ Handles graceful shutdown (Ctrl+C)
- ✅ Process isolation with multiprocessing
- ✅ Configurable enable/disable per watcher

---

## 🚀 Quick Start

### Installation

```bash
# Install rich for beautiful dashboard (optional but recommended)
pip install rich

# Manager works without rich but with basic output
```

### Start All Watchers

```bash
python scripts/watcher_manager.py
```

**What happens:**
1. Loads configuration from `config/watcher_config.json`
2. Starts all enabled watchers as background processes
3. Displays real-time dashboard with status
4. Monitors health and restarts if needed
5. Aggregates logs to daily log files

**Press Ctrl+C to stop all watchers gracefully**

---

## 📊 Dashboard

### With Rich (Recommended)

Beautiful terminal dashboard with:

```
╭────────────── Watcher Manager Dashboard ──────────────╮
│ Watcher          Status     PID    Uptime  Restarts  │
├───────────────────────────────────────────────────────┤
│ inbox_watcher    ● Running  1234   5m 30s     0      │
│ gmail_watcher    ● Running  1235   5m 28s     0      │
│ linkedin_watcher ○ Stopped  -      -          0      │
╰───────────────────────────────────────────────────────╯

╭───────────────── Recent Logs ─────────────────────────╮
│ 18:30:00 [inbox_watcher ] INFO    Started with PID... │
│ 18:30:02 [gmail_watcher ] INFO    Gmail API service...│
│ 18:30:15 [inbox_watcher ] INFO    Moved file to...    │
│ 18:31:00 [gmail_watcher ] INFO    Found 2 emails...   │
╰───────────────────────────────────────────────────────╯
```

### Without Rich (Basic Mode)

Simple text-based monitoring:

```
======================================================================
Watcher Status - 2026-02-05 18:30:00
======================================================================

[inbox_watcher]
  Status: running
  PID: 1234
  Uptime: 5m 30s
  Restarts: 0
  Errors: 0

[gmail_watcher]
  Status: running
  PID: 1235
  Uptime: 5m 28s
  Restarts: 1
  Errors: 2

======================================================================
Recent logs:
----------------------------------------------------------------------
18:30:00 [inbox_watcher] INFO: Started with PID 1234
18:30:02 [gmail_watcher] INFO: Gmail API service initialized
...
```

---

## ⚙️ Configuration

### Configuration File

**Location:** `config/watcher_config.json`

**View current configuration:**
```bash
python scripts/watcher_manager.py --config
```

### Watcher Configuration

Each watcher can be configured independently:

```json
{
  "watchers": {
    "inbox_watcher": {
      "enabled": true,                    // Enable/disable watcher
      "script": "watchers/inbox_watcher_silver.py",
      "description": "Monitors filesystem inbox",
      "restart_on_crash": true,           // Auto-restart on crash
      "max_restarts": 5,                  // Max restart attempts
      "restart_delay": 10,                // Seconds between restarts
      "health_check_interval": 30         // Health check frequency
    }
  }
}
```

### Manager Configuration

```json
{
  "manager": {
    "log_aggregation": true,              // Aggregate logs to daily files
    "status_update_interval": 2,          // Status refresh (seconds)
    "max_log_lines": 100,                 // Max logs in buffer
    "dashboard_refresh_rate": 1.0         // Dashboard refresh (Hz)
  }
}
```

### Enable/Disable Watchers

Edit `config/watcher_config.json`:

```json
{
  "watchers": {
    "inbox_watcher": {
      "enabled": true    // ← Set to false to disable
    },
    "gmail_watcher": {
      "enabled": false   // ← Disabled
    }
  }
}
```

---

## 🎮 Usage

### Start Manager

```bash
# Start with dashboard
python scripts/watcher_manager.py

# The manager will:
# 1. Start all enabled watchers
# 2. Show real-time dashboard
# 3. Monitor health
# 4. Auto-restart on crashes
# 5. Aggregate logs
```

### Check Status

```bash
# Check if manager is running
python scripts/watcher_manager.py --status
```

**Output:**
```
Watcher Status
======================================================================
Watcher manager is running (PID: 5678)
```

### Stop All Watchers

```bash
# Stop gracefully
python scripts/watcher_manager.py --stop
```

**Or press Ctrl+C in the dashboard**

### View Configuration

```bash
# Show current configuration
python scripts/watcher_manager.py --config
```

---

## 🔄 Auto-Restart Behavior

### When Watchers Restart

The manager automatically restarts watchers when:

1. **Process crashes** - Unexpected termination
2. **Heartbeat timeout** - No activity for 3x health check interval
3. **Manual restart** - After stop/start cycle

### Restart Limits

To prevent infinite restart loops:

- **Max restarts:** 5 attempts (configurable)
- **Restart delay:** 10 seconds between attempts (configurable)
- **Backoff:** Delay increases with consecutive restarts

**Example scenario:**
```
18:30:00 - gmail_watcher crashes
18:30:10 - Restart attempt 1 (after 10s delay)
18:30:20 - Crashes again
18:30:32 - Restart attempt 2 (after 12s delay)
...
18:31:00 - Max restarts reached, stops attempting
```

### Restart Configuration

Customize per watcher:

```json
{
  "restart_on_crash": true,     // Enable auto-restart
  "max_restarts": 5,            // Max attempts
  "restart_delay": 10,          // Base delay (seconds)
  "health_check_interval": 30   // Heartbeat timeout = 3x this
}
```

---

## 📝 Logging

### Aggregated Logs

All watcher logs are aggregated to daily log files:

**Location:** `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

**Format:**
```json
{
  "timestamp": "2026-02-05T18:30:00.123456",
  "watcher": "gmail_watcher",
  "level": "info",
  "message": "Found 2 important emails"
}
```

### Log Levels

- **info** - Normal operations
- **warning** - Non-critical issues
- **error** - Errors that need attention

### View Logs

```bash
# View today's logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'

# Filter by watcher
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.watcher=="gmail_watcher")'

# Filter by level
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.level=="error")'

# Count errors per watcher
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | select(.level=="error")] | group_by(.watcher) | map({watcher: .[0].watcher, count: length})'
```

---

## 🛡️ Health Monitoring

### Health Checks

The manager monitors watcher health by:

1. **Process Status** - Checking if process is alive
2. **Heartbeat** - Monitoring log output activity
3. **Error Rate** - Tracking error frequency

### Heartbeat System

Each watcher must send logs regularly. If no logs for 3x `health_check_interval`:

```
18:30:00 - Last heartbeat from gmail_watcher
18:31:30 - 90 seconds elapsed (3x 30s interval)
18:31:30 - Manager detects stale heartbeat
18:31:30 - Initiates restart
```

### Status States

- **stopped** - Not running
- **starting** - Initialization in progress
- **running** - Operating normally
- **crashed** - Process died unexpectedly
- **stopping** - Graceful shutdown in progress

---

## 🚀 Production Deployment

### Systemd Service (Linux)

**File:** `/etc/systemd/system/watcher-manager.service`

```ini
[Unit]
Description=AI Employee Watcher Manager
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/hackathon0-personal-ai-employee
ExecStart=/usr/bin/python3 scripts/watcher_manager.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Enable service
sudo systemctl enable watcher-manager

# Start service
sudo systemctl start watcher-manager

# Check status
sudo systemctl status watcher-manager

# View logs
sudo journalctl -u watcher-manager -f

# Stop service
sudo systemctl stop watcher-manager
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. **Name:** AI Employee Watcher Manager
4. **Trigger:** At startup
5. **Action:** Start a program
   - Program: `python`
   - Arguments: `scripts/watcher_manager.py`
   - Start in: `D:\hackathon0-personal-ai-employee`
6. **Settings:**
   - ✅ Run whether user is logged on or not
   - ✅ Run with highest privileges
   - ✅ If task fails, restart every 1 minute

### Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt rich

# Copy application
COPY . .

# Run manager
CMD ["python", "scripts/watcher_manager.py"]
```

**Build and run:**
```bash
docker build -t watcher-manager .
docker run -d --name watcher-manager \
  -v $(pwd)/AI_Employee_Vault:/app/AI_Employee_Vault \
  -v $(pwd)/config:/app/config \
  watcher-manager
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  watcher-manager:
    build: .
    container_name: watcher-manager
    restart: unless-stopped
    volumes:
      - ./AI_Employee_Vault:/app/AI_Employee_Vault
      - ./config:/app/config
      - ./mcp_servers/email:/app/mcp_servers/email
```

---

## 🔧 Troubleshooting

### Issue: Manager Won't Start

**Error:**
```
[ERROR] No watchers started
```

**Solutions:**
1. Check configuration: `python scripts/watcher_manager.py --config`
2. Verify at least one watcher is enabled
3. Check watcher scripts exist:
   ```bash
   ls watchers/inbox_watcher_silver.py
   ls watchers/gmail_watcher.py
   ```

### Issue: Watcher Keeps Crashing

**Symptoms:** Dashboard shows repeated restarts

**Debug steps:**
1. Check logs: `cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.level=="error")'`
2. Run watcher manually to see error:
   ```bash
   python watchers/gmail_watcher.py --test --once
   ```
3. Check watcher-specific requirements (OAuth tokens, etc.)

### Issue: Max Restarts Reached

**Message:** `Max restarts (5) reached`

**What happened:** Watcher crashed 5 times in succession

**Solutions:**
1. Fix underlying issue causing crashes
2. Increase `max_restarts` in config
3. Increase `restart_delay` to give more recovery time
4. Check watcher logs for root cause

### Issue: Rich Not Available

**Message:** `'rich' not installed. Using basic output.`

**Solution:**
```bash
pip install rich
```

**Note:** Manager works fine without rich, just with simpler output

### Issue: PID File Exists But Process Not Running

**Error when starting:**
```
Watcher manager PID file exists but process is not running
```

**Solution:**
```bash
# Remove stale PID file
rm .watcher_manager.pid

# Start manager
python scripts/watcher_manager.py
```

---

## 📊 Monitoring & Metrics

### Real-Time Metrics

The dashboard shows:
- **Status** - Current state of each watcher
- **PID** - Process ID
- **Uptime** - Time since start
- **Restarts** - Number of restart attempts
- **Errors** - Count of error logs
- **Last Heartbeat** - Time since last activity

### Historical Metrics

Query log files for trends:

```bash
# Total logs per watcher today
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | .watcher] | group_by(.) | map({watcher: .[0], count: length})'

# Error rate per hour
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.level=="error")] | group_by(.timestamp[0:13]) | map({hour: .[0].timestamp[11:13], errors: length})'

# Uptime calculation (approximate from logs)
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.message | contains("Started"))] | length'
```

### Alerts

Set up alerts based on metrics:

```bash
# Alert if too many errors
ERROR_COUNT=$(cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | select(.level=="error")] | length')
if [ $ERROR_COUNT -gt 50 ]; then
    echo "ALERT: High error count: $ERROR_COUNT"
    # Send notification
fi

# Alert if watcher not running
if ! pgrep -f "watcher_manager.py" > /dev/null; then
    echo "ALERT: Watcher manager not running"
    # Send notification
fi
```

---

## 🎯 Best Practices

### Development

1. **Test watchers individually first**
   ```bash
   python watchers/gmail_watcher.py --test --once
   ```

2. **Use dry-run modes** to validate without side effects

3. **Start with one watcher** enabled at a time

4. **Monitor logs** during initial runs

### Production

1. **Run as systemd service** for automatic startup

2. **Set appropriate restart limits** based on watcher stability

3. **Monitor dashboard regularly** or set up alerts

4. **Review aggregated logs daily** for issues

5. **Keep configuration in version control** (but not tokens!)

6. **Test recovery** by manually killing processes

7. **Document custom settings** and reasons for changes

### Configuration

1. **Start conservative** with restart limits

2. **Tune health check intervals** based on watcher behavior

3. **Adjust log buffer size** based on activity level

4. **Balance dashboard refresh rate** (performance vs. responsiveness)

---

## 🔒 Security

### Credentials

- Manager runs watchers as subprocesses
- Each watcher loads its own credentials
- No credentials stored in manager

### Process Isolation

- Each watcher runs in separate process
- Crash of one watcher doesn't affect others
- Manager can restart failed watchers independently

### Permissions

- Manager needs read access to watcher scripts
- Manager needs write access to logs directory
- Watchers need their own API credentials

---

## 📈 Scaling

### Adding New Watchers

1. **Create watcher script** following pattern
2. **Add to configuration:**
   ```json
   {
     "watchers": {
       "my_watcher": {
         "enabled": true,
         "script": "watchers/my_watcher.py",
         "description": "My custom watcher",
         "restart_on_crash": true,
         "max_restarts": 5,
         "restart_delay": 10,
         "health_check_interval": 30
       }
     }
   }
   ```
3. **Restart manager**

### Performance Tuning

**For many watchers:**
- Increase `max_log_lines` buffer
- Decrease `dashboard_refresh_rate` (e.g., 0.5 Hz)
- Increase `status_update_interval` (e.g., 5 seconds)

**For high-volume logging:**
- Decrease `max_log_lines` to reduce memory
- Implement log rotation
- Consider separate log files per watcher

---

## 📞 Support

### Logs

- **Manager logs:** Included in daily log files
- **Watcher logs:** Aggregated in daily log files
- **System logs:** `journalctl -u watcher-manager` (systemd)

### Common Issues

1. **Watcher not starting:** Check script path in config
2. **High restart count:** Check watcher logs for errors
3. **Dashboard not updating:** Check `dashboard_refresh_rate`
4. **Missing logs:** Check `log_aggregation` enabled

### Debug Mode

For detailed troubleshooting, run watcher manually:

```bash
# Test specific watcher
python watchers/gmail_watcher.py --test --once

# Check manager can load config
python scripts/watcher_manager.py --config

# Check manager status
python scripts/watcher_manager.py --status
```

---

## 🚀 Advanced Usage

### Custom Health Checks

Extend `WatcherProcess` class to add custom health checks:

```python
def custom_health_check(self) -> bool:
    """Custom health check logic."""
    # Check specific conditions
    # Return True if healthy, False if needs restart
    pass
```

### External Monitoring Integration

Export metrics for external monitoring:

```python
def export_metrics(self):
    """Export metrics to monitoring system."""
    metrics = {
        "watchers": {
            name: {
                "status": w.status.status,
                "uptime": w.get_uptime(),
                "restarts": w.status.restarts,
                "errors": w.status.error_count
            }
            for name, w in self.watchers.items()
        }
    }
    # Send to Prometheus, Datadog, etc.
```

### Webhook Notifications

Add webhook notifications on events:

```python
def notify_crash(self, watcher_name: str):
    """Send webhook notification on crash."""
    requests.post(WEBHOOK_URL, json={
        "event": "watcher_crashed",
        "watcher": watcher_name,
        "timestamp": datetime.now().isoformat()
    })
```

---

**Version:** 1.0.0
**Last Updated:** 2026-02-05
**Maintainer:** AI Employee System
