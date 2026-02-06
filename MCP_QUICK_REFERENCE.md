# MCP Servers - Quick Reference Card

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start all MCP servers
./scripts/start_mcp_servers.sh start      # Linux/macOS/WSL
scripts\start_mcp_servers.bat start       # Windows

# 2. Check status
./scripts/start_mcp_servers.sh status

# 3. Use in Claude Code
claude
> Search my Gmail for unread emails
```

---

## 📁 File Locations

| File | Path | Purpose |
|------|------|---------|
| **Project Config** | `.mcp.json` | Main config (Git tracked) |
| **Full Config** | `mcp_config.json` | Reference config |
| **Gmail Server** | `mcp_servers/email/server.js` | MCP server |
| **OAuth Creds** | `mcp_servers/email/config.json` | OAuth client |
| **OAuth Token** | `mcp_servers/email/token.json` | Access token |
| **Logs** | `mcp_servers/logs/` | All logs |
| **Startup Script** | `scripts/start_mcp_servers.*` | sh/bat |

---

## 🛠️ Startup Script Commands

### Linux/macOS/WSL
```bash
cd /path/to/hackathon0-personal-ai-employee

# Start all servers
./scripts/start_mcp_servers.sh start

# Stop all servers
./scripts/start_mcp_servers.sh stop

# Show status
./scripts/start_mcp_servers.sh status

# Restart
./scripts/start_mcp_servers.sh restart

# Health check
./scripts/start_mcp_servers.sh health

# View logs
./scripts/start_mcp_servers.sh logs
./scripts/start_mcp_servers.sh logs gmail
```

### Windows
```cmd
cd D:\hackathon0-personal-ai-employee

REM Start all servers
scripts\start_mcp_servers.bat start

REM Stop all servers
scripts\start_mcp_servers.bat stop

REM Show status
scripts\start_mcp_servers.bat status

REM Restart
scripts\start_mcp_servers.bat restart

REM Health check
scripts\start_mcp_servers.bat health

REM View logs
scripts\start_mcp_servers.bat logs
scripts\start_mcp_servers.bat logs gmail
```

---

## 🔧 Claude Code Commands

```bash
# List all MCP servers
claude mcp list

# Get server details
claude mcp get gmail

# Add new server
claude mcp add --transport stdio servername -- command

# Remove server
claude mcp remove servername

# Import from Claude Desktop
claude mcp add-from-claude-desktop

# Interactive management
claude
> /mcp
```

---

## 📊 Status Output

### Running (Green)
```
✓ gmail started successfully (PID: 12345)
  SERVER          STATUS       PID        UPTIME
  gmail           RUNNING      12345      00:05:32
```

### Stopped (Red)
```
  SERVER          STATUS       PID        UPTIME
  gmail           STOPPED      -          -
```

### Crashed (Yellow)
```
✗ gmail is not running (stale PID)
  SERVER          STATUS       PID        UPTIME
  gmail           CRASHED      12345      -
```

---

## 🔍 Troubleshooting

### Server won't start
```bash
# Check Node.js
node --version

# Check dependencies
cd mcp_servers/email && npm install

# Test manually
cd mcp_servers/email && node server.js

# View logs
tail -f mcp_servers/logs/gmail.log
```

### Claude Code not detecting
```bash
# Verify config
claude mcp list

# Check .mcp.json exists
ls -la .mcp.json

# Validate JSON
node -e "console.log(JSON.parse(require('fs').readFileSync('.mcp.json')))"
```

### OAuth errors
```bash
# Re-authenticate
cd mcp_servers/email
node auth.js

# Or use Python
python scripts/setup_gmail_oauth.py
```

---

## 🌍 Environment Variables

### Global (set before running Claude Code)
```bash
# Linux/macOS
export MCP_TIMEOUT=30000
export MCP_TOOL_TIMEOUT=120000
export MAX_MCP_OUTPUT_TOKENS=50000

# Windows
set MCP_TIMEOUT=30000
set MCP_TOOL_TIMEOUT=120000
set MAX_MCP_OUTPUT_TOKENS=50000
```

### Server-specific (in .mcp.json)
```json
{
  "env": {
    "GMAIL_CREDENTIALS_PATH": "mcp_servers/email/config.json",
    "GMAIL_TOKEN_PATH": "mcp_servers/email/token.json",
    "NODE_ENV": "production"
  }
}
```

---

## 📝 Log Files

### View logs
```bash
# Main log (all servers)
tail -f mcp_servers/logs/2026-02-05.log

# Gmail server log
tail -f mcp_servers/logs/gmail.log

# Last 50 lines
./scripts/start_mcp_servers.sh logs
./scripts/start_mcp_servers.sh logs gmail
```

### Log locations
```
mcp_servers/logs/
├── 2026-02-05.log       # Main log (today)
├── gmail.log            # Gmail server output
└── pids/
    └── gmail.pid        # Process ID
```

---

## 🔐 Security Checklist

- [ ] `config.json` and `token.json` in `.gitignore`
- [ ] File permissions: `chmod 600` on credentials
- [ ] Environment variables for secrets
- [ ] No hardcoded credentials in `.mcp.json`
- [ ] OAuth tokens stored securely

```bash
# Set permissions (Linux/macOS)
chmod 600 mcp_servers/email/config.json
chmod 600 mcp_servers/email/token.json
chmod 644 .mcp.json
```

---

## 🎯 Gmail MCP Tools

### search_emails
```
Search my Gmail for unread emails from last week
Find emails with attachments from john@example.com
```

### draft_email
```
Draft an email to team@company.com about tomorrow's meeting
Create a draft email with the weekly report
```

### send_email
```
Send an email to john@example.com thanking them for the meeting
Email the invoice to client@company.com with subject "Invoice #123"
```

---

## 🆘 Common Issues

### Issue: "Server not found"
**Fix:** `claude mcp list` to verify, add with `claude mcp add`

### Issue: "Permission denied"
**Fix:** `chmod +x scripts/start_mcp_servers.sh`

### Issue: "Port 8080 in use"
**Fix:** Kill process on 8080 or change port in OAuth config

### Issue: "Token expired"
**Fix:** Re-run `node auth.js` or `python scripts/setup_gmail_oauth.py`

### Issue: "Process not found"
**Fix:** `./scripts/start_mcp_servers.sh stop` then `start`

---

## 📚 Documentation Links

| Topic | File |
|-------|------|
| **This Reference** | `MCP_QUICK_REFERENCE.md` |
| **Full Config Guide** | `MCP_CONFIGURATION_GUIDE.md` |
| **Gmail Server** | `mcp_servers/email/README.md` |
| **Gmail Setup** | `mcp_servers/email/SETUP_GUIDE.md` |
| **Python Scripts** | `scripts/README_GMAIL_SCRIPTS.md` |
| **Complete Summary** | `GMAIL_MCP_SETUP_COMPLETE.md` |

---

## ⚡ One-Liners

```bash
# Start everything
./scripts/start_mcp_servers.sh start && claude mcp list

# Stop everything
./scripts/start_mcp_servers.sh stop

# Restart if stuck
./scripts/start_mcp_servers.sh restart

# Check health
./scripts/start_mcp_servers.sh health

# View errors
tail -n 20 mcp_servers/logs/gmail.log | grep ERROR

# Clean old logs (7+ days)
find mcp_servers/logs -name "*.log" -mtime +7 -delete
```

---

## 🎨 Status Colors

- **Green** (✓): Running, healthy, success
- **Red** (✗): Stopped, failed, error
- **Yellow** (⚠): Warning, crashed, stale
- **Blue** (ℹ): Info, processing
- **Cyan**: Headers, separators

---

## 💡 Pro Tips

1. **Always check status before debugging**
   ```bash
   ./scripts/start_mcp_servers.sh status
   ```

2. **Use health check after changes**
   ```bash
   ./scripts/start_mcp_servers.sh health
   ```

3. **Monitor logs in real-time**
   ```bash
   tail -f mcp_servers/logs/gmail.log
   ```

4. **Test server standalone first**
   ```bash
   cd mcp_servers/email && node server.js
   ```

5. **Keep logs clean**
   - Automatically rotate daily
   - Delete old logs weekly
   - Check `mcp_servers/logs/` size

---

## 🔄 Update Checklist

When updating configuration:

1. [ ] Edit `.mcp.json` or `mcp_config.json`
2. [ ] Validate JSON syntax
3. [ ] Restart servers: `./scripts/start_mcp_servers.sh restart`
4. [ ] Verify: `claude mcp list`
5. [ ] Test: Use tool in Claude Code
6. [ ] Check logs for errors
7. [ ] Commit changes (except credentials!)

---

## 📞 Getting Help

**Check logs first:**
```bash
./scripts/start_mcp_servers.sh logs
```

**Test server manually:**
```bash
cd mcp_servers/email
node server.js
# Ctrl+C to stop
```

**Verify OAuth:**
```bash
ls -la mcp_servers/email/token.json
```

**Reset everything:**
```bash
./scripts/start_mcp_servers.sh stop
rm mcp_servers/logs/pids/*.pid
./scripts/start_mcp_servers.sh start
```

---

**Print this card for quick reference!** 📄

Last Updated: February 2026
