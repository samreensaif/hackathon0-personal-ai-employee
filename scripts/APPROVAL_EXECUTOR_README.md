# Approval Executor - MCP Action Dispatcher

Automated execution system for approved actions in the AI Employee Vault.

---

## 📋 Overview

The Approval Executor watches the `AI_Employee_Vault/Approved/` folder and automatically executes approved actions via MCP (Model Context Protocol) servers. It provides robust error handling, retry logic, rate limiting, and comprehensive logging.

---

## 🎯 Features

### Core Functionality
- ✅ **Folder Watching** - Monitors Approved/ for new action files
- ✅ **Action Parsing** - Extracts metadata and action parameters
- ✅ **MCP Execution** - Calls appropriate MCP tools
- ✅ **Retry Logic** - 3 attempts with exponential backoff
- ✅ **Rate Limiting** - Max 10 actions per hour
- ✅ **Logging** - Detailed logs in JSON format
- ✅ **File Management** - Moves to Done/ or Failed/
- ✅ **Dashboard Updates** - Tracks execution history
- ✅ **Dry-Run Mode** - Safe testing without execution

### Async Performance
- Non-blocking file processing
- Concurrent action execution
- Efficient resource usage

---

## 🚀 Quick Start

### Install Dependencies

```bash
# Approval executor uses only Python standard library
# No additional dependencies needed!
python --version  # Requires Python 3.7+
```

### Run the Executor

```bash
# Normal mode (watch continuously)
python scripts/approval_executor.py

# Dry-run mode (test without execution)
python scripts/approval_executor.py --dry-run

# Process once and exit
python scripts/approval_executor.py --once

# Custom watch interval
python scripts/approval_executor.py --interval 5

# Debug mode
python scripts/approval_executor.py --debug
```

---

## 📂 File Structure

### Input: Approved Actions

Files in `AI_Employee_Vault/Approved/` should have this format:

```markdown
---
action: send_email
status: approved
email_to: recipient@example.com
email_subject: Project Update
createdAt: 2026-02-05T10:30:00
approvedAt: 2026-02-05T11:00:00
approvedBy: user@example.com
---

# Email Body

Hello,

This is the content of the email.

Best regards
```

### Output: Results

**Success** → Moved to `AI_Employee_Vault/Done/`
**Failure** → Moved to `AI_Employee_Vault/Failed/`

**Logs** → `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

---

## 🔧 Supported Actions

### 1. send_email

Send an email via Gmail MCP server.

**Metadata:**
```yaml
action: send_email
email_to: recipient@example.com
email_subject: Subject line
email_cc: cc@example.com  # Optional
```

**Body:** Email content (supports HTML)

**Example:**
```markdown
---
action: send_email
status: approved
email_to: client@example.com
email_subject: Weekly Report
approvedAt: 2026-02-05T11:00:00
---

<p>Please find attached the weekly report.</p>
<p>Best regards,<br>AI Employee</p>
```

### 2. draft_email

Create a draft email (not sent).

**Metadata:**
```yaml
action: draft_email
email_to: recipient@example.com
email_subject: Subject line
```

**Body:** Email content

### 3. search_emails

Search Gmail for emails.

**Metadata:**
```yaml
action: search_emails
search_query: from:boss@company.com is:unread
max_results: 10  # Optional, default: 10
```

### 4. post_linkedin (Coming Soon)

Post to LinkedIn.

**Metadata:**
```yaml
action: post_linkedin
visibility: public  # public, connections, private
```

**Body:** Post content

---

## ⚙️ Configuration

### Environment Variables

```bash
# Optional: Override defaults
export APPROVAL_WATCH_INTERVAL=5
export APPROVAL_MAX_RETRIES=3
export APPROVAL_RATE_LIMIT=10
```

### Rate Limiting

**Default:** 10 actions per hour

**How it works:**
- Tracks action timestamps in a sliding window
- Prevents execution if limit reached
- Provides wait time for next available slot

**Check status:**
```python
rate_limiter.get_status()
# {
#   'current_actions': 5,
#   'max_actions': 10,
#   'can_execute': True,
#   'wait_time': 0
# }
```

### Retry Logic

**Strategy:** Exponential backoff

**Configuration:**
- Max retries: 3
- Initial delay: 2 seconds
- Backoff multiplier: 2x

**Delay sequence:** 2s → 4s → 8s

**Example:**
```
Attempt 1: Execute immediately
Attempt 1 fails → Wait 2s
Attempt 2: Execute
Attempt 2 fails → Wait 4s
Attempt 3: Execute
Attempt 3 fails → Mark as failed
```

---

## 📊 Logging

### Log Format

**Location:** `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

**Entry Structure:**
```json
{
  "timestamp": "2026-02-05T11:00:00.123456",
  "action": "execute_approved_action",
  "file": "send_welcome_email.md",
  "action_type": "send_email",
  "success": true,
  "attempts": 1,
  "result": "completed"
}
```

**Failed Entry:**
```json
{
  "timestamp": "2026-02-05T11:00:00.123456",
  "action": "execute_approved_action",
  "file": "invalid_action.md",
  "action_type": "send_email",
  "success": false,
  "attempts": 3,
  "result": "failed",
  "error": "Invalid email address"
}
```

**Rate Limited:**
```json
{
  "timestamp": "2026-02-05T11:00:00.123456",
  "action": "execute_approved_action",
  "file": "email_11.md",
  "action_type": "send_email",
  "success": false,
  "result": "failed",
  "rate_limited": true,
  "error": "Rate limit exceeded"
}
```

---

## 📈 Dashboard Updates

The executor updates `AI_Employee_Vault/Dashboard.md` with recent actions.

**Format:**
```markdown
## Recent Actions

- [2026-02-05 11:00:00] send_email - ✓ Success - welcome_email.md
- [2026-02-05 11:05:00] draft_email - ✓ Success - draft_report.md
- [2026-02-05 11:10:00] send_email - ✗ Failed - invalid_email.md
```

---

## 🧪 Testing

### Dry-Run Mode

Test without executing real actions:

```bash
python scripts/approval_executor.py --dry-run
```

**What happens:**
- ✓ Files are parsed
- ✓ Actions are validated
- ✓ Logs are written
- ✗ No MCP tools executed
- ✗ Files are NOT moved
- ✗ Dashboard is NOT updated

**Output:**
```
[DRY RUN] Would execute send_email with args: {'to': '...', 'subject': '...'}
[DRY RUN] Would move welcome_email.md to Done/
[DRY RUN] Would update Dashboard.md
```

### Create Test Files

```bash
# Create test action
cat > AI_Employee_Vault/Approved/test_email.md << 'EOF'
---
action: send_email
status: approved
email_to: test@example.com
email_subject: Test Email
createdAt: 2026-02-05T11:00:00
---

This is a test email from the approval executor.
EOF

# Run executor once
python scripts/approval_executor.py --once --dry-run
```

### Manual Testing

```bash
# 1. Create test file
cp examples/sample_email_action.md AI_Employee_Vault/Approved/

# 2. Run executor in dry-run
python scripts/approval_executor.py --once --dry-run

# 3. Check logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq

# 4. Run for real
python scripts/approval_executor.py --once

# 5. Verify file moved
ls AI_Employee_Vault/Done/
```

---

## 🐛 Troubleshooting

### Issue: Files Not Processing

**Check 1:** Verify file format
```bash
# File must have .md extension
ls AI_Employee_Vault/Approved/*.md

# File must have metadata
head -10 AI_Employee_Vault/Approved/your_file.md
```

**Check 2:** Validate metadata
```python
python -c "
from scripts.approval_executor import ActionFileParser
from pathlib import Path
data = ActionFileParser.parse_file(Path('AI_Employee_Vault/Approved/your_file.md'))
print(data)
"
```

### Issue: Rate Limit Reached

**Symptom:**
```
WARNING: Rate limit reached. Need to wait 2345.6s
```

**Solution 1:** Wait for window to reset
```bash
# Check rate limiter status
python -c "
from scripts.approval_executor import RateLimiter
limiter = RateLimiter(10, 3600)
print(limiter.get_status())
"
```

**Solution 2:** Increase limit (if appropriate)
```bash
# Edit MAX_ACTIONS_PER_HOUR in script
# Or set environment variable
export APPROVAL_RATE_LIMIT=20
```

### Issue: MCP Server Not Found

**Symptom:**
```
ERROR: Failed to execute tool send_email: Server failed to start
```

**Solution:**
```bash
# Verify server exists
ls mcp_servers/email/server.js

# Test server manually
cd mcp_servers/email
node server.js

# Check dependencies
npm install
```

### Issue: Permission Denied

**Symptom:**
```
ERROR: Failed to move file: Permission denied
```

**Solution:**
```bash
# Check folder permissions
ls -la AI_Employee_Vault/

# Fix permissions
chmod 755 AI_Employee_Vault/Approved/
chmod 755 AI_Employee_Vault/Done/
chmod 755 AI_Employee_Vault/Failed/
```

---

## 🔒 Security

### File Validation

- ✅ Validates action types (whitelist)
- ✅ Checks required metadata fields
- ✅ Sanitizes file paths
- ✅ Prevents path traversal

### Rate Limiting

- ✅ Prevents abuse (10 actions/hour)
- ✅ Protects Gmail API quotas
- ✅ Sliding window enforcement

### Error Handling

- ✅ Catches all exceptions
- ✅ No sensitive data in logs
- ✅ Safe file operations
- ✅ Graceful degradation

---

## 📚 Advanced Usage

### Custom MCP Server

```python
# In approval_executor.py, modify:
MCP_EMAIL_SERVER = PROJECT_ROOT / "mcp_servers" / "custom" / "server.js"
```

### Add New Action Type

1. **Add to supported actions:**
```python
SUPPORTED_ACTIONS = [
    'send_email',
    'your_new_action',  # Add here
]
```

2. **Implement mapping:**
```python
def _map_action_to_tool(self, action_data):
    if action_type == 'your_new_action':
        return self._map_your_new_action(metadata, body)
```

3. **Add mapper method:**
```python
def _map_your_new_action(self, metadata, body):
    arguments = {
        'param1': metadata.get('field1'),
        'param2': body
    }
    return ('mcp_tool_name', arguments)
```

### Integrate with CI/CD

```yaml
# GitHub Actions example
- name: Process Approved Actions
  run: |
    python scripts/approval_executor.py --once
  timeout-minutes: 10
```

---

## 📊 Monitoring

### Check Execution Status

```bash
# View today's logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.action=="execute_approved_action")'

# Count successes
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | select(.success==true)] | length'

# Count failures
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '[.[] | select(.success==false)] | length'

# View errors
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.success==false) | .error'
```

### Rate Limit Status

```bash
# Check current usage
python -c "
from scripts.approval_executor import RateLimiter
limiter = RateLimiter(10, 3600)
# ... load previous actions ...
status = limiter.get_status()
print(f'Used: {status[\"current_actions\"]}/{status[\"max_actions\"]}')
print(f'Can execute: {status[\"can_execute\"]}')
print(f'Wait time: {status[\"wait_time\"]:.0f}s')
"
```

---

## 🎯 Best Practices

### 1. Test in Dry-Run First
```bash
# Always test new actions
python scripts/approval_executor.py --dry-run --once
```

### 2. Monitor Logs Regularly
```bash
# Daily log review
tail -f AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### 3. Set Up Monitoring
```bash
# Cron job to check for failures
*/30 * * * * /path/to/check_failures.sh
```

### 4. Backup Before Changes
```bash
# Backup Approved folder
cp -r AI_Employee_Vault/Approved/ AI_Employee_Vault/Approved.backup/
```

### 5. Use Meaningful Filenames
```bash
# Good: send_welcome_email_to_john_2026-02-05.md
# Bad: email.md, action1.md, test.md
```

---

## 📞 Support

### Documentation
- **Main README:** `scripts/approval_executor.py` (docstrings)
- **This Guide:** `scripts/APPROVAL_EXECUTOR_README.md`
- **MCP Docs:** https://modelcontextprotocol.io/

### Logs
- **Execution logs:** `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **Dashboard:** `AI_Employee_Vault/Dashboard.md`

### Debugging
```bash
# Enable debug mode
python scripts/approval_executor.py --debug

# Verbose output shows:
# - File parsing details
# - MCP communication
# - Retry attempts
# - Rate limit checks
```

---

## 🚀 Future Enhancements

### Planned Features
- [ ] LinkedIn MCP integration
- [ ] Calendar event creation
- [ ] Slack message posting
- [ ] Custom webhook actions
- [ ] Email with attachments
- [ ] Scheduled actions (cron-like)
- [ ] Action priorities
- [ ] Parallel execution

### Configuration File
Future version will support `approval_executor_config.json`:
```json
{
  "rate_limit": {
    "max_actions": 10,
    "window_seconds": 3600
  },
  "retry": {
    "max_attempts": 3,
    "initial_delay": 2,
    "backoff_multiplier": 2
  },
  "watch": {
    "interval": 3,
    "folders": ["Approved"]
  }
}
```

---

**Last Updated:** February 2026
**Version:** 1.0.0
**Status:** Production Ready
