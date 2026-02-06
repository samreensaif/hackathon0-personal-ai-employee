# Gmail Watcher - Usage Examples

Real-world examples of using the Gmail Watcher.

---

## 📋 Installation

```bash
# Install dependencies
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Or use requirements file
pip install -r scripts/requirements-gmail.txt
```

---

## 🔧 Initial Setup

### Step 1: Configure OAuth Credentials

```bash
# Run OAuth setup wizard
python scripts/setup_gmail_oauth.py
```

This will:
1. Open your browser for Google sign-in
2. Request Gmail permissions
3. Save token to `mcp_servers/email/token.json`

### Step 2: Test Configuration

```bash
# Run test script
python watchers/test_gmail_watcher.py
```

Expected output:
```
======================================================================
Gmail Watcher Test Script
======================================================================

[1/5] Checking dependencies...
  ✓ google-auth installed
  ✓ google-oauth2 installed
  ✓ google-api-python-client installed

[2/5] Checking credentials files...
  ✓ Credentials file found: mcp_servers/email/config.json
  ✓ Credentials file appears valid
  ✓ Token file found: mcp_servers/email/token.json

[3/5] Testing Gmail API authentication...
  ✓ Gmail API authentication successful
  ✓ Connected to Gmail API

[4/5] Testing email query (dry-run)...
  Query: is:unread in:inbox (is:important OR from:(@client.com OR @customer.com)...
  ✓ Found 3 important email(s)

  Sample emails found:
    1. [HIGH] Urgent: Client needs proposal by EOD
       From: client@acme.com
    2. [MEDIUM] Invoice #1234 for January
       From: billing@vendor.com
    3. [LOW] FYI: Server maintenance this weekend
       From: ops@company.com

[5/5] Verifying configuration...
  ✓ Needs_Action folder exists: AI_Employee_Vault/Needs_Action
  ✓ Logs folder exists: AI_Employee_Vault/Logs

======================================================================
Test Summary
======================================================================

✅ All tests passed!

Configuration:
  - Credentials: mcp_servers/email/config.json
  - Token: mcp_servers/email/token.json
  - Output: AI_Employee_Vault/Needs_Action
  - Logs: AI_Employee_Vault/Logs

Next steps:
  1. Review filter configuration in watchers/gmail_watcher.py
  2. Customize IMPORTANT_KEYWORDS and CLIENT_DOMAINS
  3. Run in test mode: python watchers/gmail_watcher.py --test --once
  4. Start monitoring: python watchers/gmail_watcher.py

For detailed setup instructions, see:
  watchers/GMAIL_WATCHER_SETUP.md

======================================================================
```

---

## 🎬 Example 1: Test Mode (Safe Testing)

Run once in test mode to see what would be processed without marking emails as read:

```bash
python watchers/gmail_watcher.py --test --once
```

**Output:**
```
======================================================================
Gmail Inbox Watcher for AI Employee System
======================================================================

[TEST MODE] Emails will NOT be marked as read

2026-02-05 18:30:00 [INFO] Gmail Watcher initialized (test_mode=True, dry_run=False)
2026-02-05 18:30:00 [INFO] Loaded existing credentials from token.json
2026-02-05 18:30:00 [OK] Gmail API service initialized

2026-02-05 18:30:00 [INFO] Starting email check cycle...
2026-02-05 18:30:01 [INFO] Searching with query: is:unread in:inbox (is:important OR from:(@client.com...
2026-02-05 18:30:02 [OK] Found 3 important email(s)

2026-02-05 18:30:02 [INFO] Processing: Urgent: Client needs proposal by EOD...
2026-02-05 18:30:02 [OK] Created task file: email_20260205_183002_Urgent_Client_needs_proposal.md
2026-02-05 18:30:02 [INFO] [TEST MODE] Would mark message abc123xyz as read

2026-02-05 18:30:03 [INFO] Processing: Invoice #1234 for January services...
2026-02-05 18:30:03 [OK] Created task file: email_20260205_183003_Invoice_1234_for_January.md
2026-02-05 18:30:03 [INFO] [TEST MODE] Would mark message def456abc as read

2026-02-05 18:30:04 [INFO] Processing: Help needed with API integration...
2026-02-05 18:30:04 [OK] Created task file: email_20260205_183004_Help_needed_with_API.md
2026-02-05 18:30:04 [INFO] [TEST MODE] Would mark message ghi789def as read

2026-02-05 18:30:05 [OK] Cycle complete: 3/3 emails processed

✅ Processed 3 email(s)
```

**What happened:**
- ✅ 3 task files created in `Needs_Action/`
- ✅ Email metadata extracted and saved
- ❌ Emails NOT marked as read (test mode)

**Check created tasks:**
```bash
ls -lt AI_Employee_Vault/Needs_Action/email_*
```

---

## 🎬 Example 2: Dry Run (Validation Only)

Check what emails would be processed without creating tasks or marking as read:

```bash
python watchers/gmail_watcher.py --dry-run --once
```

**Output:**
```
======================================================================
Gmail Inbox Watcher for AI Employee System
======================================================================

[DRY RUN] No task files will be created, no emails marked as read

2026-02-05 18:35:00 [INFO] Gmail Watcher initialized (test_mode=False, dry_run=True)
2026-02-05 18:35:00 [INFO] Loaded existing credentials from token.json
2026-02-05 18:35:00 [OK] Gmail API service initialized

2026-02-05 18:35:00 [INFO] Starting email check cycle...
2026-02-05 18:35:01 [INFO] Searching with query: is:unread in:inbox (is:important OR from:(@client.com...
2026-02-05 18:35:02 [OK] Found 3 important email(s)

2026-02-05 18:35:02 [INFO] Processing: Urgent: Client needs proposal by EOD...
2026-02-05 18:35:02 [INFO] [DRY-RUN] Would create task for: Urgent: Client needs proposal by EOD
2026-02-05 18:35:02 [INFO] [DRY-RUN] Would mark message abc123xyz as read

2026-02-05 18:35:03 [INFO] Processing: Invoice #1234 for January services...
2026-02-05 18:35:03 [INFO] [DRY-RUN] Would create task for: Invoice #1234 for January services
2026-02-05 18:35:03 [INFO] [DRY-RUN] Would mark message def456abc as read

2026-02-05 18:35:04 [INFO] Processing: Help needed with API integration...
2026-02-05 18:35:04 [INFO] [DRY-RUN] Would create task for: Help needed with API integration
2026-02-05 18:35:04 [INFO] [DRY-RUN] Would mark message ghi789def as read

2026-02-05 18:35:05 [OK] Cycle complete: 3/3 emails processed

✅ Processed 3 email(s)
```

**What happened:**
- ❌ No task files created (dry run)
- ❌ Emails NOT marked as read (dry run)
- ✅ Validated query and email detection works

---

## 🎬 Example 3: Production Mode

Start continuous monitoring in production:

```bash
python watchers/gmail_watcher.py
```

**Output:**
```
======================================================================
Gmail Inbox Watcher for AI Employee System
======================================================================

2026-02-05 18:40:00 [INFO] Gmail Watcher initialized (test_mode=False, dry_run=False)
2026-02-05 18:40:00 [INFO] Loaded existing credentials from token.json
2026-02-05 18:40:00 [OK] Gmail API service initialized

2026-02-05 18:40:00 [INFO] Starting continuous monitoring (poll interval: 120s)...
2026-02-05 18:40:00 [INFO] Press Ctrl+C to stop

2026-02-05 18:40:00 [INFO] Starting email check cycle...
2026-02-05 18:40:01 [INFO] Searching with query: is:unread in:inbox (is:important OR...
2026-02-05 18:40:02 [OK] Found 2 important email(s)

2026-02-05 18:40:02 [INFO] Processing: URGENT: Production server down...
2026-02-05 18:40:02 [OK] Created task file: email_20260205_184002_URGENT_Production_server_down.md
2026-02-05 18:40:02 [OK] Marked message xyz123abc as read

2026-02-05 18:40:03 [INFO] Processing: Payment received for invoice #1234...
2026-02-05 18:40:03 [OK] Created task file: email_20260205_184003_Payment_received.md
2026-02-05 18:40:03 [OK] Marked message abc789xyz as read

2026-02-05 18:40:04 [OK] Cycle complete: 2/2 emails processed

2026-02-05 18:40:04 [INFO] Sleeping for 120 seconds...

[... 2 minutes later ...]

2026-02-05 18:42:04 [INFO] Starting email check cycle...
2026-02-05 18:42:05 [INFO] Searching with query: is:unread in:inbox (is:important OR...
2026-02-05 18:42:06 [INFO] No new important emails found

2026-02-05 18:42:06 [INFO] Sleeping for 120 seconds...

[... continues monitoring ...]
```

**Press Ctrl+C to stop:**
```
^C
2026-02-05 18:44:10 [INFO] Stopping watcher...
2026-02-05 18:44:10 [INFO] Total emails processed this session: 2
```

---

## 📧 Example Task File Created

**File:** `AI_Employee_Vault/Needs_Action/email_20260205_184002_URGENT_Production_server_down.md`

```markdown
---
createdAt: 2026-02-05T18:40:02.123456
source: gmail_watcher
status: needs_action
type: email_task
priority: high
email_metadata:
  message_id: xyz123abc
  thread_id: thread_xyz123
  from: ops@company.com
  subject: "URGENT: Production server down"
  date: Wed, 5 Feb 2026 18:30:00 -0800
  is_important: true
  is_client: false
  labels: ["INBOX", "IMPORTANT", "UNREAD"]
---

# Email: URGENT: Production server down

**From:** Operations Team <ops@company.com>
**Date:** Wed, 5 Feb 2026 18:30:00 -0800
**Priority:** HIGH

## Email Preview

Our production server (srv-prod-01) went down at 18:25. Database connections failing. Need immediate attention. Users cannot access the application. ETA for fix needed...

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

**Message ID:** xyz123abc
**Thread ID:** thread_xyz123
```

---

## 📊 Monitoring Examples

### Check Processing Statistics

```bash
# Count emails processed today
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.source=="gmail_watcher" and .action=="email_processed")] | length'

# Output: 15
```

### View Last 5 Processed Emails

```bash
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.source=="gmail_watcher" and .action=="email_processed")] | .[-5:]'
```

**Output:**
```json
[
  {
    "timestamp": "2026-02-05T18:40:02.123456",
    "action": "email_processed",
    "source": "gmail_watcher",
    "message_id": "xyz123abc",
    "from": "ops@company.com",
    "subject": "URGENT: Production server down",
    "priority": "high",
    "task_file": "AI_Employee_Vault/Needs_Action/email_20260205_184002_URGENT_Production_server_down.md",
    "test_mode": false,
    "dry_run": false
  },
  ...
]
```

### Check Rate Limit Status

The watcher tracks rate limits internally. Check recent processing:

```bash
# Count emails processed in last hour
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq --arg hour "$(date -u -d '1 hour ago' +'%Y-%m-%dT%H')" \
  '[.[] | select(.source=="gmail_watcher" and .action=="email_processed" and (.timestamp | startswith($hour)))] | length'
```

---

## 🔧 Customization Examples

### Example 1: Add More Important Keywords

Edit `watchers/gmail_watcher.py`:

```python
IMPORTANT_KEYWORDS = [
    # Urgency keywords
    'urgent', 'asap', 'critical', 'emergency', 'immediate', 'deadline',

    # Financial keywords
    'invoice', 'payment', 'overdue', 'refund', 'charge',

    # Support keywords
    'help', 'problem', 'issue', 'bug', 'error', 'down',

    # Business keywords
    'proposal', 'contract', 'deal', 'meeting', 'call',

    # Custom keywords
    'quarterly report', 'board meeting', 'regulatory'
]
```

### Example 2: Configure Client Domains

```python
CLIENT_DOMAINS = [
    # Major clients
    '@acmecorp.com',
    '@bigclient.com',
    '@importantpartner.com',

    # VIP individuals
    'ceo@anywhere.com',
    'john.doe@anywhere.com'
]
```

### Example 3: Adjust Priority Levels

```python
PRIORITY_KEYWORDS = {
    'high': [
        'urgent', 'asap', 'critical', 'emergency', 'immediate',
        'deadline', 'production', 'outage', 'down'
    ],
    'medium': [
        'invoice', 'payment', 'help', 'problem', 'issue',
        'meeting', 'proposal', 'contract'
    ],
    'low': [
        'fyi', 'info', 'update', 'newsletter'
    ]
}
```

### Example 4: Change Polling Frequency

```python
# Check every minute (high volume)
POLL_INTERVAL = 60

# Check every 5 minutes (low volume)
POLL_INTERVAL = 300

# Check every 10 minutes (very low volume)
POLL_INTERVAL = 600
```

---

## 🐛 Troubleshooting Examples

### Issue: Token Expired

**Error:**
```
2026-02-05 18:45:00 [ERROR] Failed to refresh credentials: invalid_grant
2026-02-05 18:45:00 [WARN] Please run: python scripts/setup_gmail_oauth.py
```

**Fix:**
```bash
python scripts/setup_gmail_oauth.py
```

### Issue: No Emails Detected

**Scenario:** Watcher running but not finding important emails you know exist.

**Debug:**
```bash
# Run dry-run to see query
python watchers/gmail_watcher.py --dry-run --once

# Look at the query being used
# Expected: is:unread in:inbox (is:important OR from:(@client.com...))
```

**Verify in Gmail:**
1. Go to Gmail web interface
2. Paste the query in search box
3. See what emails match
4. Adjust filters if needed

### Issue: Rate Limit Hit

**Output:**
```
2026-02-05 19:00:00 [WARN] Rate limit exceeded: 50/50 per hour
2026-02-05 19:00:00 [INFO] No new important emails found
```

**What happened:**
- Processed 50 emails in the past hour
- Rate limit prevents processing more
- Will resume after 1 hour

**Solutions:**
1. Wait for rate limit to reset
2. Increase `MAX_EMAILS_PER_HOUR` (if needed)
3. Improve filters to be more selective

---

## 🚀 Advanced Usage

### Running as Systemd Service (Linux)

**File:** `/etc/systemd/system/gmail-watcher.service`

```ini
[Unit]
Description=Gmail Inbox Watcher for AI Employee
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/hackathon0-personal-ai-employee
ExecStart=/usr/bin/python3 watchers/gmail_watcher.py
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Enable service
sudo systemctl enable gmail-watcher

# Start service
sudo systemctl start gmail-watcher

# Check status
sudo systemctl status gmail-watcher

# View logs
sudo journalctl -u gmail-watcher -f

# Stop service
sudo systemctl stop gmail-watcher
```

### Docker Container

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY scripts/requirements-gmail.txt .
RUN pip install --no-cache-dir -r requirements-gmail.txt

# Copy application
COPY watchers/ ./watchers/
COPY scripts/ ./scripts/
COPY AI_Employee_Vault/ ./AI_Employee_Vault/
COPY mcp_servers/email/config.json ./mcp_servers/email/
COPY mcp_servers/email/token.json ./mcp_servers/email/

# Run watcher
CMD ["python", "watchers/gmail_watcher.py"]
```

**Build and run:**
```bash
docker build -t gmail-watcher .
docker run -d --name gmail-watcher \
  -v $(pwd)/AI_Employee_Vault:/app/AI_Employee_Vault \
  gmail-watcher
```

---

## 📈 Success Metrics

Track these metrics to ensure the watcher is working well:

1. **Processing Rate:** ~50-100 emails/day detected
2. **False Positives:** <10% of emails shouldn't be tasks
3. **False Negatives:** <5% of important emails missed
4. **Response Time:** Tasks created within 2 minutes of email arrival
5. **Error Rate:** <1% of processing attempts fail

**Check metrics:**
```bash
# Today's processing count
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.source=="gmail_watcher")] | length'

# Success rate
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | \
  jq '[.[] | select(.source=="gmail_watcher")] | group_by(.action) | map({action: .[0].action, count: length})'
```

---

**Version:** 1.0.0
**Last Updated:** 2026-02-05
