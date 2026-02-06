# Watcher Manager - Quick Reference

Production-ready process manager for all AI Employee watchers.

---

## 🚀 Quick Start

### Linux/Mac

```bash
# Start all watchers
./scripts/start_watchers.sh

# Stop all watchers
./scripts/start_watchers.sh stop

# Check status
./scripts/start_watchers.sh status
```

### Windows

```cmd
REM Start all watchers
scripts\start_watchers.bat

REM Stop all watchers
scripts\start_watchers.bat stop

REM Check status
scripts\start_watchers.bat status
```

### Python Direct

```bash
# Start manager with dashboard
python scripts/watcher_manager.py

# Stop all watchers
python scripts/watcher_manager.py --stop

# Check status
python scripts/watcher_manager.py --status

# View configuration
python scripts/watcher_manager.py --config
```

---

## 📊 Dashboard

### With Rich (Recommended)

```bash
# Install rich for beautiful dashboard
pip install rich

# Start manager
python scripts/watcher_manager.py
```

**You'll see:**
- Real-time watcher status table
- Live log stream
- Color-coded status indicators
- Uptime and health metrics

### Without Rich (Basic Mode)

Works automatically if rich not installed:
- Simple text-based monitoring
- Refreshes every 2 seconds
- Shows all essential information

---

## ⚙️ Configuration

### Enable/Disable Watchers

Edit `config/watcher_config.json`:

```json
{
  "watchers": {
    "inbox_watcher": {
      "enabled": true     // ← Set to false to disable
    },
    "gmail_watcher": {
      "enabled": true
    },
    "linkedin_watcher": {
      "enabled": false    // ← Disabled by default
    }
  }
}
```

### Restart Settings

```json
{
  "restart_on_crash": true,      // Auto-restart crashed watchers
  "max_restarts": 5,             // Max restart attempts
  "restart_delay": 10,           // Seconds between restarts
  "health_check_interval": 30    // Health check frequency
}
```

---

## 🔄 What It Does

### Process Management

1. **Starts all enabled watchers** as background processes
2. **Monitors health** with heartbeat checks
3. **Auto-restarts** crashed watchers (up to max_restarts)
4. **Aggregates logs** to daily JSON files
5. **Shows real-time dashboard** with status
6. **Handles graceful shutdown** (Ctrl+C stops all)

### Health Monitoring

- **Process Status** - Checks if process is alive
- **Heartbeat** - Monitors log activity
- **Error Rate** - Tracks error frequency
- **Auto-restart** - Restarts on crash or timeout

### Logging

All logs aggregated to:
```
AI_Employee_Vault/Logs/YYYY-MM-DD.json
```

Format:
```json
{
  "timestamp": "2026-02-05T18:30:00.123456",
  "watcher": "gmail_watcher",
  "level": "info",
  "message": "Found 2 important emails"
}
```

---

## 📋 Managed Watchers

### Inbox Watcher
- **Script:** `watchers/inbox_watcher_silver.py`
- **Purpose:** Monitors filesystem inbox
- **Default:** Enabled

### Gmail Watcher
- **Script:** `watchers/gmail_watcher.py`
- **Purpose:** Monitors Gmail inbox
- **Default:** Enabled

### LinkedIn Watcher
- **Script:** `watchers/linkedin_watcher.py`
- **Purpose:** Monitors LinkedIn notifications
- **Default:** Disabled (not implemented yet)

---

## 🛡️ Error Handling

### Auto-Restart

If a watcher crashes:
1. Manager detects crash immediately
2. Waits `restart_delay` seconds
3. Attempts restart
4. Increments restart counter
5. Stops after `max_restarts` attempts

### Max Restarts Reached

If watcher crashes too many times:
- Manager stops restart attempts
- Status shows "crashed"
- Manual intervention needed
- Check logs for root cause

---

## 📊 Monitoring

### Real-Time

Dashboard shows:
- Watcher status (running, stopped, crashed)
- Process ID (PID)
- Uptime
- Restart count
- Error count
- Last heartbeat time

### Historical

Query log files:

```bash
# View today's logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'

# Filter by watcher
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '.[] | select(.watcher=="gmail_watcher")'

# Count errors
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.level=="error")] | length'
```

---

## 🚀 Production Deployment

### Systemd Service (Linux)

```bash
# Copy service file
sudo cp systemd/watcher-manager.service /etc/systemd/system/

# Enable and start
sudo systemctl enable watcher-manager
sudo systemctl start watcher-manager

# Check status
sudo systemctl status watcher-manager

# View logs
sudo journalctl -u watcher-manager -f
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Import `windows/watcher-manager.xml`
3. Update paths in task
4. Start task

### Docker

```bash
# Build image
docker build -t watcher-manager .

# Run container
docker run -d --name watcher-manager \
  -v $(pwd)/AI_Employee_Vault:/app/AI_Employee_Vault \
  -v $(pwd)/config:/app/config \
  watcher-manager
```

---

## 🔧 Troubleshooting

### Manager Won't Start

**Check:**
1. Configuration file exists: `config/watcher_config.json`
2. At least one watcher enabled
3. Watcher scripts exist

**Fix:**
```bash
# Verify config
python scripts/watcher_manager.py --config

# Check watcher files
ls watchers/*.py
```

### Watcher Keeps Crashing

**Check logs:**
```bash
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '.[] | select(.level=="error")'
```

**Test watcher manually:**
```bash
python watchers/gmail_watcher.py --test --once
```

### Max Restarts Reached

**What happened:** Watcher crashed 5 times

**Fix:**
1. Check logs for error patterns
2. Fix underlying issue
3. Restart manager

### Dashboard Not Updating

**Check:**
1. Rich installed: `pip list | grep rich`
2. Terminal supports colors
3. Dashboard refresh rate in config

---

## 📚 Documentation

- **Complete Guide:** [WATCHER_MANAGER_GUIDE.md](WATCHER_MANAGER_GUIDE.md)
- **Configuration:** [config/watcher_config.json](../config/watcher_config.json)
- **Individual Watchers:** [watchers/README.md](../watchers/README.md)

---

## 🎯 Key Features

✅ **Single Command** - Start/stop all watchers
✅ **Auto-Restart** - Crashed watchers restart automatically
✅ **Health Monitoring** - Heartbeat checks and error tracking
✅ **Aggregated Logs** - All logs in one place
✅ **Real-Time Dashboard** - Beautiful terminal interface
✅ **Graceful Shutdown** - Ctrl+C stops all cleanly
✅ **Process Isolation** - Each watcher in separate process
✅ **Production Ready** - Systemd, Docker, Windows support

---

## 💡 Tips

1. **Start with one watcher** to test configuration
2. **Monitor dashboard** during initial runs
3. **Check logs regularly** for errors
4. **Tune restart settings** based on stability
5. **Use rich** for better experience: `pip install rich`
6. **Run as service** in production for auto-start

---

## 📞 Quick Commands

```bash
# Start
python scripts/watcher_manager.py

# Stop
python scripts/watcher_manager.py --stop

# Status
python scripts/watcher_manager.py --status

# Config
python scripts/watcher_manager.py --config

# Logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'
```

---

**Version:** 1.0.0
**Author:** AI Employee System
**License:** MIT
