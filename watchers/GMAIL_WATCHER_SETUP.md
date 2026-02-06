# Gmail Watcher Setup Guide

Complete setup instructions for the Gmail Inbox Watcher.

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Gmail Account** with API access enabled
3. **Google Cloud Project** (can use existing one from Email MCP)

---

## 🔧 Installation

### Step 1: Install Required Python Packages

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Or install from requirements file:

```bash
pip install -r scripts/requirements-gmail.txt
```

### Step 2: Configure Gmail API Credentials

#### Option A: Use Existing Email MCP Credentials

If you've already set up the Email MCP server, you can reuse those credentials:

```bash
# The watcher looks for credentials at:
# mcp_servers/email/config.json
# mcp_servers/email/token.json
```

**Verify files exist:**
```bash
ls -la mcp_servers/email/config.json
ls -la mcp_servers/email/token.json
```

If `token.json` doesn't exist, run the OAuth setup:

```bash
python scripts/setup_gmail_oauth.py
```

#### Option B: Set Up New Credentials

If you don't have Gmail API credentials yet:

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Gmail API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "AI Employee Gmail Watcher"
   - Click "Create"

4. **Download Credentials**
   - Click the download icon next to your new OAuth client
   - Save as `mcp_servers/email/config.json`

5. **Run OAuth Flow**
   ```bash
   python scripts/setup_gmail_oauth.py
   ```
   - This will open your browser
   - Sign in with your Gmail account
   - Grant permissions
   - Token will be saved to `mcp_servers/email/token.json`

### Step 3: Configure Filters (Optional)

Edit `watchers/gmail_watcher.py` to customize filtering:

```python
# Important keywords to search for
IMPORTANT_KEYWORDS = [
    'urgent', 'asap', 'critical', 'emergency', 'immediate',
    'invoice', 'payment', 'help', 'problem', 'issue', 'deadline'
]

# Client email domains
CLIENT_DOMAINS = [
    '@client.com', '@customer.com', '@partner.com'
]

# Polling interval (seconds)
POLL_INTERVAL = 120  # 2 minutes
```

### Step 4: Test the Watcher

Run in test mode to verify everything works without modifying emails:

```bash
python watchers/gmail_watcher.py --test --once
```

Expected output:
```
======================================================================
Gmail Inbox Watcher for AI Employee System
======================================================================

[TEST MODE] Emails will NOT be marked as read

2026-02-05 18:30:00 [INFO] Gmail Watcher initialized (test_mode=True, dry_run=False)
2026-02-05 18:30:00 [INFO] Loaded existing credentials from token.json
2026-02-05 18:30:00 [OK] Gmail API service initialized
2026-02-05 18:30:00 [INFO] Starting email check cycle...
2026-02-05 18:30:01 [INFO] Searching with query: is:unread in:inbox (is:important OR from:(@client.com OR ...
2026-02-05 18:30:02 [OK] Found 3 important email(s)
2026-02-05 18:30:02 [INFO] Processing: Urgent: Client needs proposal...
2026-02-05 18:30:02 [OK] Created task file: email_20260205_183002_Urgent_Client_needs_proposal.md
2026-02-05 18:30:02 [INFO] [TEST MODE] Would mark message abc123 as read
...
2026-02-05 18:30:05 [OK] Cycle complete: 3/3 emails processed

✅ Processed 3 email(s)
```

---

## 🚀 Usage

### Run Modes

#### Normal Mode (Production)
Processes emails, creates tasks, and marks emails as read:

```bash
python watchers/gmail_watcher.py
```

Press `Ctrl+C` to stop.

#### Test Mode
Creates tasks but does NOT mark emails as read (for testing):

```bash
python watchers/gmail_watcher.py --test
```

#### Dry Run Mode
Does not create tasks or mark emails as read (validation only):

```bash
python watchers/gmail_watcher.py --dry-run
```

#### Once Mode
Process emails once and exit (no continuous monitoring):

```bash
python watchers/gmail_watcher.py --once
```

#### Combined Modes
```bash
# Test mode + once (safe testing)
python watchers/gmail_watcher.py --test --once

# Dry run + once (just check for emails)
python watchers/gmail_watcher.py --dry-run --once
```

---

## 📁 Output

### Task Files Created

Location: `AI_Employee_Vault/Needs_Action/`

Format: `email_YYYYMMDD_HHMMSS_subject.md`

Example:
```markdown
---
createdAt: 2026-02-05T18:30:00.000000
source: gmail_watcher
status: needs_action
type: email_task
priority: high
email_metadata:
  message_id: abc123xyz
  thread_id: thread_abc123
  from: client@example.com
  subject: "Urgent: Need proposal by EOD"
  date: Wed, 5 Feb 2026 10:00:00 -0800
  is_important: true
  is_client: true
  labels: ["INBOX", "IMPORTANT", "UNREAD"]
---

# Email: Urgent: Need proposal by EOD

**From:** John Doe <client@example.com>
**Date:** Wed, 5 Feb 2026 10:00:00 -0800
**Priority:** HIGH

## Email Preview

Hi, we need the Q1 proposal by end of day today. This is urgent...

## Action Required

This email has been flagged as important and requires attention.

### Suggested Actions:
- [ ] Read full email in Gmail
- [ ] Draft response if needed
- [ ] Categorize and archive
- [ ] Forward to appropriate team member
- [ ] Add to task list for follow-up

## Notes

_Add any notes or context here_

---

**Message ID:** abc123xyz
**Thread ID:** thread_abc123
```

### Logs

Location: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

Example log entry:
```json
{
  "timestamp": "2026-02-05T18:30:00.000000",
  "action": "email_processed",
  "source": "gmail_watcher",
  "message_id": "abc123xyz",
  "from": "client@example.com",
  "subject": "Urgent: Need proposal by EOD",
  "priority": "high",
  "task_file": "AI_Employee_Vault/Needs_Action/email_20260205_183000_Urgent_Need_proposal.md",
  "test_mode": false,
  "dry_run": false
}
```

---

## ⚙️ Configuration

### Filtering

The watcher uses a Gmail search query to filter important emails:

**Base Query:**
```
is:unread in:inbox (is:important OR from:(@client.com OR @customer.com) OR (subject:urgent OR subject:invoice OR ...))
```

**Customize in code:**

```python
# Important keywords in subject line
IMPORTANT_KEYWORDS = [
    'urgent', 'asap', 'critical', 'emergency', 'immediate',
    'invoice', 'payment', 'help', 'problem', 'issue', 'deadline'
]

# Client email domains (emails from these are always important)
CLIENT_DOMAINS = [
    '@client.com', '@customer.com', '@partner.com'
]

# Priority levels based on keywords
PRIORITY_KEYWORDS = {
    'high': ['urgent', 'asap', 'critical', 'emergency', 'immediate', 'deadline'],
    'medium': ['invoice', 'payment', 'help', 'problem', 'issue'],
    'low': []
}
```

### Polling Interval

Change how often the watcher checks for new emails:

```python
POLL_INTERVAL = 120  # seconds (default: 2 minutes)
```

Recommended values:
- **Production:** 120-300 seconds (2-5 minutes)
- **Development:** 60 seconds (1 minute)
- **High volume:** 60 seconds
- **Low volume:** 300 seconds (5 minutes)

### Rate Limiting

Prevent processing too many emails:

```python
MAX_EMAILS_PER_HOUR = 50  # Max emails to process per hour
MAX_RESULTS = 50          # Max emails to fetch per poll
```

---

## 🔄 Integration with Task Processor

Once the Gmail watcher creates task files in `Needs_Action/`, the task processor will:

1. Detect the new email task
2. Categorize it based on content and priority
3. Route to appropriate folder:
   - `Pending_Approval/` if requires email response
   - `High_Priority/` if urgent
   - `Needs_Action/` for normal processing

**Example flow:**
```
Gmail Inbox (unread important email)
    ↓
Gmail Watcher detects and creates task
    ↓
Task file created in Needs_Action/
    ↓
Task Processor analyzes task
    ↓
Routes based on priority and keywords
    ↓
Creates execution plan
    ↓
Waits for human action or approval
```

---

## 🛡️ Error Handling

### OAuth Token Expired

**Error:**
```
[ERROR] Failed to refresh credentials: invalid_grant
```

**Solution:**
```bash
# Re-run OAuth setup
python scripts/setup_gmail_oauth.py
```

### Gmail API Error

**Error:**
```
[ERROR] Gmail API error: <HttpError 403...>
```

**Solutions:**
1. Check Gmail API is enabled in Google Cloud Console
2. Verify OAuth scopes include:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
3. Check API quota limits

### Rate Limit Exceeded

**Error:**
```
[WARN] Rate limit exceeded: 50/50 per hour
```

**Solution:**
- Wait for the rate limit window to reset (1 hour)
- Adjust `MAX_EMAILS_PER_HOUR` in configuration

### No Emails Found

**Message:**
```
[INFO] No new important emails found
```

**Troubleshooting:**
1. Check your filter configuration
2. Verify emails are unread and in inbox
3. Test with dry-run to see query:
   ```bash
   python watchers/gmail_watcher.py --dry-run --once
   ```

---

## 📊 Monitoring

### Check Watcher Status

View recent logs:
```bash
# Today's log
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.source=="gmail_watcher")'

# Count processed emails today
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | select(.source=="gmail_watcher" and .action=="email_processed")] | length'
```

### View Created Tasks

```bash
# List email tasks
ls -lt AI_Employee_Vault/Needs_Action/email_*

# Count email tasks
ls AI_Employee_Vault/Needs_Action/email_* | wc -l
```

---

## 🔧 Troubleshooting

### Issue: Credentials Not Found

**Error:**
```
[ERROR] Credentials file not found: mcp_servers/email/config.json
```

**Fix:**
1. Ensure `mcp_servers/email/config.json` exists
2. Run: `python scripts/setup_gmail_oauth.py`

### Issue: Emails Not Being Processed

**Checks:**
1. Are emails unread? `is:unread`
2. Are they in inbox? `in:inbox`
3. Do they match filters? (important, client domain, keywords)
4. Check logs for errors

**Debug:**
```bash
# Run in test mode to see what would be processed
python watchers/gmail_watcher.py --test --once
```

### Issue: Task Processor Not Picking Up Tasks

**Checks:**
1. Is task processor running?
   ```bash
   python scripts/runner_silver.py
   ```
2. Are task files in `Needs_Action/`?
   ```bash
   ls AI_Employee_Vault/Needs_Action/email_*
   ```
3. Do task files have valid YAML frontmatter?

---

## 🚀 Running as Background Service

### Linux/Mac (systemd)

Create service file: `/etc/systemd/system/gmail-watcher.service`

```ini
[Unit]
Description=Gmail Inbox Watcher for AI Employee
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/hackathon0-personal-ai-employee
ExecStart=/usr/bin/python3 watchers/gmail_watcher.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gmail-watcher
sudo systemctl start gmail-watcher
sudo systemctl status gmail-watcher
```

View logs:
```bash
sudo journalctl -u gmail-watcher -f
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Gmail Inbox Watcher"
4. Trigger: At startup
5. Action: Start a program
   - Program: `python`
   - Arguments: `watchers/gmail_watcher.py`
   - Start in: `D:\hackathon0-personal-ai-employee`
6. Finish

### Docker (Optional)

Create `Dockerfile.gmail-watcher`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "watchers/gmail_watcher.py"]
```

Build and run:
```bash
docker build -f Dockerfile.gmail-watcher -t gmail-watcher .
docker run -d --name gmail-watcher \
  -v $(pwd)/AI_Employee_Vault:/app/AI_Employee_Vault \
  -v $(pwd)/mcp_servers/email:/app/mcp_servers/email \
  gmail-watcher
```

---

## 📈 Best Practices

1. **Start with test mode** to verify configuration
2. **Use dry-run** to test filters without side effects
3. **Monitor logs daily** for errors and rate limits
4. **Adjust filters** based on your email patterns
5. **Run once mode** initially before continuous monitoring
6. **Set up alerts** for watcher failures (systemd, monitoring tools)
7. **Review processed tasks** regularly to refine filters
8. **Keep credentials secure** (never commit token.json)

---

## 🔒 Security

- **Never commit** `token.json` or `config.json` with real credentials
- **Use environment variables** for sensitive data in production
- **Restrict OAuth scopes** to minimum required:
  - `gmail.readonly` - Read emails
  - `gmail.modify` - Mark as read
- **Review permissions** regularly in Google Account settings
- **Rotate credentials** periodically
- **Monitor access logs** in Google Cloud Console

---

## 📞 Support

- **Gmail API Documentation:** https://developers.google.com/gmail/api
- **OAuth 2.0 Guide:** https://developers.google.com/identity/protocols/oauth2
- **Rate Limits:** https://developers.google.com/gmail/api/reference/quota

---

**Version:** 1.0.0
**Last Updated:** 2026-02-05
**Maintainer:** AI Employee System
