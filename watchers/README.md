# Watchers

Automated monitoring services that detect events and create tasks for the AI Employee system.

---

## 📚 Available Watchers

### 1. Inbox Watcher (`inbox_watcher_silver.py`)

**Purpose:** Monitors `AI_Employee_Vault/Inbox/` for new markdown files

**Features:**
- Watches filesystem for new `.md` files
- Adds metadata to files
- Moves files from root to Inbox
- Automatically triggers task processor

**Usage:**
```bash
python watchers/inbox_watcher_silver.py
```

---

### 2. Gmail Watcher (`gmail_watcher.py`) 🆕

**Purpose:** Monitors Gmail inbox for important emails and creates tasks automatically

**Features:**
- Polls Gmail API every 2 minutes
- Filters by importance, client domains, and keywords
- Creates task files in `Needs_Action/`
- Marks processed emails as read
- Rate limiting (50 emails/hour)
- OAuth token refresh handling
- Test mode and dry-run mode

**Quick Start:**
```bash
# Install dependencies
pip install -r scripts/requirements-gmail.txt

# Setup OAuth (one-time)
python scripts/setup_gmail_oauth.py

# Test configuration
python watchers/test_gmail_watcher.py

# Run in test mode
python watchers/gmail_watcher.py --test --once

# Start monitoring
python watchers/gmail_watcher.py
```

**Documentation:**
- Setup Guide: [`GMAIL_WATCHER_SETUP.md`](GMAIL_WATCHER_SETUP.md)
- Test Script: [`test_gmail_watcher.py`](test_gmail_watcher.py)

---

## 🚀 Running Watchers

### Individual Watchers

```bash
# Inbox watcher (filesystem)
python watchers/inbox_watcher_silver.py

# Gmail watcher (email)
python watchers/gmail_watcher.py
```

### Multiple Watchers Simultaneously

Use separate terminal windows or background processes:

**Terminal 1:**
```bash
python watchers/inbox_watcher_silver.py
```

**Terminal 2:**
```bash
python watchers/gmail_watcher.py
```

**Or run in background:**
```bash
# Start inbox watcher in background
nohup python watchers/inbox_watcher_silver.py > logs/inbox_watcher.log 2>&1 &

# Start gmail watcher in background
nohup python watchers/gmail_watcher.py > logs/gmail_watcher.log 2>&1 &

# View background processes
ps aux | grep watcher

# Stop watchers
pkill -f inbox_watcher
pkill -f gmail_watcher
```

---

## 📊 Comparison

| Feature | Inbox Watcher | Gmail Watcher |
|---------|---------------|---------------|
| **Source** | Filesystem | Gmail API |
| **Poll Interval** | 3 seconds | 120 seconds (2 min) |
| **Trigger** | File creation | Unread important email |
| **Auth** | None | OAuth 2.0 |
| **Rate Limit** | None | 50 emails/hour |
| **Test Mode** | No | Yes |
| **Dry Run** | No | Yes |
| **Dependencies** | None | Google APIs |

---

## 🔄 Integration Flow

```
External Event (Email, File Drop)
    ↓
Watcher Detects Event
    ↓
Creates Task File in Needs_Action/
    ↓
Task Processor Detects New Task
    ↓
Analyzes and Categorizes Task
    ↓
Routes to Appropriate Folder
    ↓
Creates Execution Plan
    ↓
Waits for Human Action/Approval
```

---

## 📁 Directory Structure

```
watchers/
├── inbox_watcher.py              # Basic inbox watcher
├── inbox_watcher_silver.py       # Enhanced inbox watcher
├── gmail_watcher.py              # Gmail API watcher (NEW)
├── test_gmail_watcher.py         # Gmail watcher test script
├── GMAIL_WATCHER_SETUP.md        # Gmail setup guide
└── README.md                     # This file
```

---

## ⚙️ Configuration

### Inbox Watcher

Edit `inbox_watcher_silver.py`:

```python
POLL_INTERVAL = 3  # seconds
AUTO_PROCESS = True  # Auto-trigger task processor
```

### Gmail Watcher

Edit `gmail_watcher.py`:

```python
# Polling
POLL_INTERVAL = 120  # seconds (2 minutes)
MAX_RESULTS = 50     # max emails per poll

# Rate limiting
MAX_EMAILS_PER_HOUR = 50

# Filtering
IMPORTANT_KEYWORDS = [
    'urgent', 'asap', 'critical', 'emergency', 'immediate',
    'invoice', 'payment', 'help', 'problem', 'issue', 'deadline'
]

CLIENT_DOMAINS = [
    '@client.com', '@customer.com', '@partner.com'
]
```

---

## 🛡️ Error Handling

Both watchers include comprehensive error handling:

### Inbox Watcher
- File read errors → Skip file, log error
- Move errors → Retry, log error
- Metadata errors → Skip metadata, process file

### Gmail Watcher
- OAuth token expired → Auto-refresh
- API errors → Log and continue
- Rate limit exceeded → Wait for reset
- Network errors → Retry with backoff

---

## 📊 Monitoring

### Check Watcher Status

```bash
# View today's logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.'

# Count tasks created by each watcher
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | .source] | group_by(.) | map({source: .[0], count: length})'

# Check inbox watcher activity
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.source=="inbox")'

# Check gmail watcher activity
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.source=="gmail_watcher")'
```

### View Created Tasks

```bash
# List all tasks
ls -lt AI_Employee_Vault/Needs_Action/

# Count tasks by type
ls AI_Employee_Vault/Needs_Action/ | grep -c email_  # Email tasks
ls AI_Employee_Vault/Needs_Action/ | grep -c -v email_  # Other tasks
```

---

## 🔧 Troubleshooting

### Inbox Watcher Issues

**Problem:** Watcher not detecting files

**Solutions:**
1. Check file is in correct directory (`AI_Employee_Vault/Inbox/`)
2. Verify file has `.md` extension
3. Check file permissions
4. Look for errors in console output

---

### Gmail Watcher Issues

**Problem:** Authentication failed

**Solutions:**
1. Run OAuth setup: `python scripts/setup_gmail_oauth.py`
2. Verify `mcp_servers/email/config.json` has valid credentials
3. Check Gmail API is enabled in Google Cloud Console
4. Verify OAuth scopes match

**Problem:** No emails found

**Solutions:**
1. Check emails are unread (`is:unread`)
2. Verify emails are in inbox (`in:inbox`)
3. Review filter configuration (keywords, domains)
4. Test with dry-run: `python watchers/gmail_watcher.py --dry-run --once`

**Problem:** Rate limit exceeded

**Solutions:**
1. Wait for rate limit window to reset (1 hour)
2. Adjust `MAX_EMAILS_PER_HOUR` in configuration
3. Increase `POLL_INTERVAL` to check less frequently

---

## 🚀 Best Practices

### Development
1. Start with test mode (`--test`)
2. Use dry-run mode (`--dry-run`) to validate filters
3. Run once mode (`--once`) before continuous monitoring
4. Monitor logs for errors

### Production
1. Run watchers as background services
2. Set up log rotation
3. Configure alerts for failures
4. Monitor rate limits
5. Review and adjust filters regularly

### Security
1. Never commit OAuth tokens (`token.json`)
2. Use environment variables for sensitive config
3. Restrict OAuth scopes to minimum required
4. Rotate credentials periodically
5. Monitor access logs

---

## 📈 Future Watchers

Potential watchers to implement:

- **Slack Watcher** - Monitor Slack channels for @mentions
- **GitHub Watcher** - Monitor GitHub issues and PRs
- **Calendar Watcher** - Monitor Google Calendar for upcoming events
- **Drive Watcher** - Monitor Google Drive for new files
- **Webhook Watcher** - Receive webhooks from external services
- **Database Watcher** - Monitor database for changes
- **RSS Watcher** - Monitor RSS feeds for new articles

---

## 📞 Support

- **Inbox Watcher:** See code comments in `inbox_watcher_silver.py`
- **Gmail Watcher:** See [`GMAIL_WATCHER_SETUP.md`](GMAIL_WATCHER_SETUP.md)
- **Logs:** Check `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **Issues:** Report in project repository

---

**Version:** 1.0.0
**Last Updated:** 2026-02-05
**Maintainer:** AI Employee System
