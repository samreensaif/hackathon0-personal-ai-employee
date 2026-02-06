# MCP Server Configuration Guide for Claude Code

Complete guide for configuring and managing MCP servers with Claude Code CLI.

---

## 📋 Table of Contents

1. [Configuration Files](#configuration-files)
2. [Setup Instructions](#setup-instructions)
3. [Startup Scripts](#startup-scripts)
4. [Health Monitoring](#health-monitoring)
5. [Troubleshooting](#troubleshooting)

---

## Configuration Files

### 1. Project Configuration: `.mcp.json`

**Location:** `D:\hackathon0-personal-ai-employee\.mcp.json`

**Purpose:** Project-scoped MCP servers (shared with team via Git)

**Content:**
```json
{
  "mcpServers": {
    "gmail": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp_servers/email/server.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "${PROJECT_ROOT}/mcp_servers/email/config.json",
        "GMAIL_TOKEN_PATH": "${PROJECT_ROOT}/mcp_servers/email/token.json",
        "NODE_ENV": "production"
      },
      "timeout": 30000
    }
  }
}
```

### 2. Standalone Configuration: `mcp_config.json`

**Location:** `D:\hackathon0-personal-ai-employee\mcp_config.json`

**Purpose:** Complete configuration with logging, health checks, and security settings

**Features:**
- Global timeout settings
- Logging configuration
- Health check settings
- Security policies
- Metadata tracking

---

## Setup Instructions

### Step 1: Choose Configuration Scope

Claude Code supports three configuration scopes:

#### Option A: Project Scope (Recommended for Teams)

Use `.mcp.json` in project root - shared via Git:

```bash
# Already created at project root
cd D:\hackathon0-personal-ai-employee

# Claude Code will automatically detect .mcp.json
```

**Pros:**
- Version controlled
- Shared with team
- Consistent across environments

**Cons:**
- Credentials must not be committed
- Requires environment variables

#### Option B: User Scope (Personal Use)

Add to your personal Claude Code config:

```bash
# macOS/Linux
~/.claude.json

# Windows
%USERPROFILE%\.claude.json
```

Add the `mcpServers` section from `.mcp.json` to this file.

**Pros:**
- Personal configuration
- Works across all projects
- Can include credentials (not recommended)

**Cons:**
- Not shared with team
- Manual setup on each machine

#### Option C: Import from File

```bash
# Import the mcp_config.json
claude mcp add-json gmail '@mcp_config.json#mcpServers.gmail'
```

### Step 2: Verify Configuration

Check if Claude Code detects your server:

```bash
# List all configured servers
claude mcp list

# Expected output:
# gmail (stdio) - Gmail MCP Server - Send, draft, and search emails
```

### Step 3: Test Server Connection

```bash
# Get detailed info about the server
claude mcp get gmail

# Expected output shows:
# - Type: stdio
# - Command: node mcp_servers/email/server.js
# - Environment variables
# - Capabilities
```

---

## Startup Scripts

### For Linux/macOS/WSL: `start_mcp_servers.sh`

**Location:** `scripts/start_mcp_servers.sh`

**Usage:**

```bash
# Make executable (first time only)
chmod +x scripts/start_mcp_servers.sh

# Start all servers
./scripts/start_mcp_servers.sh start

# Stop all servers
./scripts/start_mcp_servers.sh stop

# Check status
./scripts/start_mcp_servers.sh status

# Restart servers
./scripts/start_mcp_servers.sh restart

# Health check
./scripts/start_mcp_servers.sh health

# View logs
./scripts/start_mcp_servers.sh logs          # Main log
./scripts/start_mcp_servers.sh logs gmail    # Gmail server log
```

**Features:**
- ✅ Colored terminal output
- ✅ Background process management
- ✅ PID tracking
- ✅ Graceful shutdown
- ✅ Health monitoring
- ✅ Log management
- ✅ Automatic log rotation

### For Windows: `start_mcp_servers.bat`

**Location:** `scripts\start_mcp_servers.bat`

**Usage:**

```cmd
REM Start all servers
scripts\start_mcp_servers.bat start

REM Stop all servers
scripts\start_mcp_servers.bat stop

REM Check status
scripts\start_mcp_servers.bat status

REM Restart servers
scripts\start_mcp_servers.bat restart

REM Health check
scripts\start_mcp_servers.bat health

REM View logs
scripts\start_mcp_servers.bat logs           REM Main log
scripts\start_mcp_servers.bat logs gmail     REM Gmail server log
```

**Features:**
- ✅ Windows 10+ ANSI color support
- ✅ Background process management
- ✅ PID tracking in files
- ✅ Force kill if needed
- ✅ Health monitoring
- ✅ PowerShell log viewing

---

## Health Monitoring

### Automatic Health Checks

The startup scripts include health monitoring:

1. **Process Health**
   - Checks if PID is still running
   - Detects crashed processes
   - Cleans stale PID files

2. **Startup Verification**
   - Waits 2 seconds after start
   - Verifies process is alive
   - Shows startup errors

3. **Status Reporting**
   - Running servers: Green
   - Stopped servers: Red
   - Crashed servers: Yellow
   - Shows PID and uptime

### Manual Health Check

```bash
# Linux/macOS/WSL
./scripts/start_mcp_servers.sh health

# Windows
scripts\start_mcp_servers.bat health
```

**Output Example:**
```
==========================================
Health Check
==========================================

  Checking gmail... ✓ Healthy

✓ All servers healthy
```

### Log Monitoring

**Log Locations:**

```
mcp_servers/logs/
├── 2026-02-05.log          # Main log (dated)
├── gmail.log               # Gmail server output
└── pids/
    └── gmail.pid           # Process ID
```

**Viewing Logs:**

```bash
# Last 50 lines of main log
./scripts/start_mcp_servers.sh logs

# Last 50 lines of gmail log
./scripts/start_mcp_servers.sh logs gmail

# Real-time monitoring (Linux/macOS)
tail -f mcp_servers/logs/gmail.log

# Real-time monitoring (Windows)
powershell -Command "Get-Content mcp_servers\logs\gmail.log -Wait"
```

---

## Troubleshooting

### Server Won't Start

**Check 1: Verify Node.js**
```bash
node --version  # Should show v16+
```

**Check 2: Check Dependencies**
```bash
cd mcp_servers/email
npm install
```

**Check 3: Test Server Manually**
```bash
cd mcp_servers/email
node server.js
# Should show: [INFO] Gmail MCP Server is running on stdio
```

**Check 4: View Error Logs**
```bash
# Linux/macOS
cat mcp_servers/logs/gmail.log

# Windows
type mcp_servers\logs\gmail.log
```

### Claude Code Not Detecting Server

**Check 1: Verify Configuration**
```bash
claude mcp list
# Should show "gmail" server
```

**Check 2: Check File Location**
```bash
# Verify .mcp.json exists
ls -la .mcp.json  # Linux/macOS
dir .mcp.json     # Windows
```

**Check 3: Validate JSON**
```bash
# Test JSON syntax
node -e "console.log(JSON.parse(require('fs').readFileSync('.mcp.json', 'utf8')))"
```

**Check 4: Check Permissions**
```bash
# Linux/macOS - ensure files are readable
chmod 644 .mcp.json
chmod 644 mcp_config.json
```

### Server Crashes After Start

**Check 1: OAuth Tokens**
```bash
# Verify token exists
ls mcp_servers/email/token.json

# Re-run OAuth if needed
cd mcp_servers/email
node auth.js
```

**Check 2: Environment Variables**
```bash
# Check if paths are correct
echo $PROJECT_ROOT  # Linux/macOS
echo %PROJECT_ROOT% # Windows
```

**Check 3: Port Conflicts**
```bash
# Check if port 8080 is in use (for OAuth callback)
netstat -an | grep 8080  # Linux/macOS
netstat -an | findstr 8080  # Windows
```

### Startup Script Errors

**Linux/macOS Issues:**

```bash
# Permission denied
chmod +x scripts/start_mcp_servers.sh

# Command not found
./scripts/start_mcp_servers.sh start
# Instead of:
# scripts/start_mcp_servers.sh start
```

**Windows Issues:**

```cmd
REM Execution policy
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

REM Path issues - use backslashes
scripts\start_mcp_servers.bat start

REM ANSI colors not showing
REM Requires Windows 10+ and modern terminal
```

### Log Files Growing Too Large

**Automatic Rotation:**

The scripts use dated log files that rotate daily:
- `2026-02-05.log`
- `2026-02-06.log`
- etc.

**Manual Cleanup:**

```bash
# Delete logs older than 7 days (Linux/macOS)
find mcp_servers/logs -name "*.log" -mtime +7 -delete

# Delete logs older than 7 days (Windows PowerShell)
Get-ChildItem mcp_servers\logs -Filter *.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item
```

**Configuration:**

Edit in `mcp_config.json`:
```json
{
  "logging": {
    "maxFileSize": "10MB",
    "maxFiles": 7
  }
}
```

---

## Environment Variables

### Global Environment Variables

Set these before starting Claude Code:

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

### Server-Specific Environment Variables

Defined in configuration files:

```json
{
  "env": {
    "GMAIL_CREDENTIALS_PATH": "mcp_servers/email/config.json",
    "GMAIL_TOKEN_PATH": "mcp_servers/email/token.json",
    "NODE_ENV": "production",
    "LOG_LEVEL": "info"
  }
}
```

### Variable Expansion

`.mcp.json` supports environment variable expansion:

```json
{
  "env": {
    "CONFIG_PATH": "${HOME}/config/gmail.json",
    "DATA_DIR": "${PROJECT_ROOT}/data",
    "API_KEY": "${GMAIL_API_KEY:-default_key}"
  }
}
```

**Syntax:**
- `${VAR}` - Use environment variable
- `${VAR:-default}` - Use VAR or default if not set

---

## Security Best Practices

### 1. Credential Management

**DO:**
- ✅ Use environment variables for secrets
- ✅ Store tokens in `.gitignore`d files
- ✅ Use `${VAR}` expansion in config
- ✅ Set restrictive file permissions (600)

**DON'T:**
- ❌ Commit credentials to Git
- ❌ Hardcode secrets in `.mcp.json`
- ❌ Share token files
- ❌ Use world-readable permissions

### 2. File Permissions

```bash
# Linux/macOS
chmod 600 mcp_servers/email/config.json
chmod 600 mcp_servers/email/token.json
chmod 644 .mcp.json  # Can be shared

# Verify
ls -la mcp_servers/email/*.json
```

### 3. Network Security

For HTTP MCP servers (future):

```json
{
  "security": {
    "validateCertificates": true,
    "allowedOrigins": ["localhost", "127.0.0.1"],
    "maxRequestSize": "50MB"
  }
}
```

### 4. Process Isolation

The startup scripts run servers as child processes:
- Isolated from main shell
- Clean shutdown on script exit
- No persistent background daemons
- PID tracking for management

---

## Claude Code Integration

### Using MCP Servers in Claude Code

Once configured, use natural language:

```
# Search emails
Search my Gmail for unread messages from last week

# Draft email
Draft an email to team@company.com about tomorrow's meeting

# Send email
Send an email to john@example.com thanking them for the meeting
```

### Interactive Management

Within Claude Code session:

```bash
# List available MCP servers
/mcp

# Shows:
# - gmail (3 tools available)
#   - send_email
#   - draft_email
#   - search_emails
```

### OAuth Management

For servers requiring OAuth:

```bash
# Trigger OAuth flow
/mcp

# Select server → Authenticate
# Browser opens for consent
# Tokens stored securely
```

---

## Advanced Configuration

### Multiple Servers

Add more servers to `.mcp.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp_servers/email/server.js"]
    },
    "calendar": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp_servers/calendar/server.js"]
    },
    "slack": {
      "type": "http",
      "url": "https://api.slack.com/mcp",
      "headers": {
        "Authorization": "Bearer ${SLACK_TOKEN}"
      }
    }
  }
}
```

Update startup scripts to include new servers.

### Remote HTTP Servers

For HTTP-based MCP servers:

```json
{
  "remote-api": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-API-Version": "v1"
    },
    "oauth": {
      "clientId": "${OAUTH_CLIENT_ID}",
      "callbackPort": 8080
    }
  }
}
```

### Conditional Loading

Load servers based on environment:

```json
{
  "mcpServers": {
    "gmail-prod": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp_servers/email/server.js"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "gmail-dev": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp_servers/email/server.js"],
      "env": {
        "NODE_ENV": "development",
        "LOG_LEVEL": "debug"
      }
    }
  },
  "settings": {
    "enabledMcpjsonServers": ["gmail-${NODE_ENV:-prod}"]
  }
}
```

---

## Quick Reference

### Common Commands

```bash
# List servers
claude mcp list

# Get server details
claude mcp get gmail

# Add new server
claude mcp add --transport stdio gmail -- node mcp_servers/email/server.js

# Remove server
claude mcp remove gmail

# Import from Claude Desktop
claude mcp add-from-claude-desktop
```

### Startup Script Commands

```bash
# Linux/macOS/WSL
./scripts/start_mcp_servers.sh [start|stop|status|restart|health|logs]

# Windows
scripts\start_mcp_servers.bat [start|stop|status|restart|health|logs]
```

### File Locations

```
Project Root/
├── .mcp.json                    # Project config (Git tracked)
├── mcp_config.json              # Standalone config (reference)
├── mcp_servers/
│   ├── email/
│   │   ├── server.js           # Gmail MCP server
│   │   ├── config.json         # OAuth credentials (ignored)
│   │   └── token.json          # OAuth tokens (ignored)
│   └── logs/
│       ├── YYYY-MM-DD.log      # Main log
│       ├── gmail.log           # Server log
│       └── pids/
│           └── gmail.pid       # Process ID
└── scripts/
    ├── start_mcp_servers.sh    # Linux/macOS script
    └── start_mcp_servers.bat   # Windows script
```

---

## Next Steps

1. ✅ **Configuration created** - `.mcp.json` and `mcp_config.json`
2. ✅ **Startup scripts ready** - sh and bat versions
3. ⬜ **Test configuration** - `claude mcp list`
4. ⬜ **Start servers** - `./scripts/start_mcp_servers.sh start`
5. ⬜ **Verify health** - `./scripts/start_mcp_servers.sh health`
6. ⬜ **Test in Claude Code** - Run natural language commands

---

## Support

- **Claude Code Docs:** https://code.claude.com/docs/en/mcp.md
- **MCP Specification:** https://modelcontextprotocol.io/
- **Gmail Server README:** `mcp_servers/email/README.md`
- **Scripts Guide:** `scripts/README_GMAIL_SCRIPTS.md`

---

**Last Updated:** February 2026
**Version:** 1.0.0
**Status:** Production Ready
