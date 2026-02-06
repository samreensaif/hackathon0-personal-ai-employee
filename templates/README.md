# Approval Templates

Templates for generating approval requests with MCP execution details.

---

## 📋 Available Templates

### 1. approval_email.md

**Purpose:** Email sending approval requests

**Use for:**
- Sending external emails
- Emails with attachments
- Bulk email operations
- Any email requiring review

**Key Fields:**
- `email_to` - Recipient address
- `email_subject` - Subject line
- `email_body` - Full email content
- `mcp_params` - MCP execution parameters

### 2. approval_draft.md

**Purpose:** Email draft creation approvals

**Use for:**
- Creating drafts for later review
- Template emails
- Reports that need final review

**Key Fields:**
- `email_to` - Recipient
- `email_subject` - Subject
- Body content for draft

### 3. approval_search.md

**Purpose:** Email search approvals

**Use for:**
- Reading sensitive emails
- Searching for specific information
- Email monitoring tasks

**Key Fields:**
- `search_query` - Gmail query syntax
- `max_results` - Number of results

---

## 🔧 Usage

### Method 1: Use Generator Script (Recommended)

```bash
# Generate email approval
python scripts/generate_approval.py email \
    --to "client@example.com" \
    --subject "Invoice for January" \
    --body "Please find attached your invoice..." \
    --output "AI_Employee_Vault/Pending_Approval/send_invoice.md"

# Generate draft approval
python scripts/generate_approval.py draft \
    --to "team@company.com" \
    --subject "Weekly Report" \
    --body "Report content here..." \
    --output "AI_Employee_Vault/Pending_Approval/weekly_report.md"

# Generate search approval
python scripts/generate_approval.py search \
    --query "from:boss@company.com is:unread" \
    --max-results 5 \
    --output "AI_Employee_Vault/Pending_Approval/search_urgent.md"
```

### Method 2: Manual Copy and Edit

```bash
# Copy template
cp templates/approval_email.md AI_Employee_Vault/Pending_Approval/my_action.md

# Edit file and replace {{VARIABLES}}
# - {{RECIPIENT_EMAIL}} → actual email
# - {{EMAIL_SUBJECT}} → actual subject
# - {{EMAIL_BODY}} → actual content
```

### Method 3: Programmatic Generation

```python
from scripts.generate_approval import ApprovalTemplateGenerator

# Create generator
generator = ApprovalTemplateGenerator('email')

# Generate approval
content = generator.generate(
    variables={
        'RECIPIENT_EMAIL': 'client@example.com',
        'EMAIL_SUBJECT': 'Project Update',
        'EMAIL_BODY': 'Update content...'
    },
    output_path=Path('AI_Employee_Vault/Pending_Approval/update.md')
)
```

---

## 📝 Template Variables

### Common Variables (All Templates)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `CREATED_TIMESTAMP` | Creation time | No | Now |
| `EXPIRES_TIMESTAMP` | Expiry time | No | +48h |
| `PRIORITY_LEVEL` | Priority (low/medium/high) | No | medium |
| `ORIGINAL_TASK_FILE` | Source task file | No | unknown |
| `APPROVAL_REASON` | Why approval needed | No | Default reason |

### Email-Specific Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `RECIPIENT_EMAIL` | Recipient address | Yes | client@example.com |
| `EMAIL_SUBJECT` | Subject line | Yes | Invoice for January |
| `EMAIL_BODY` | Email content | Yes | Dear Client,... |
| `EMAIL_CC` | CC addresses | No | manager@company.com |
| `ATTACHMENT_PATH_1` | Attachment file | No | ./files/invoice.pdf |
| `ATTACHMENT_NAME_1` | Display name | No | Invoice.pdf |

### Search-Specific Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SEARCH_QUERY` | Gmail query | Yes | from:boss@company.com |
| `MAX_RESULTS` | Max results | No | 10 |
| `QUERY_EXPLANATION` | Human explanation | No | Auto-generated |

---

## 🎯 Integration with Task Processors

### Silver Tier Processor

Update `scripts/runner_silver.py` to use templates:

```python
from scripts.generate_approval import ApprovalTemplateGenerator

def create_approval_request(task_data):
    """Create approval request using template."""
    generator = ApprovalTemplateGenerator('email')

    variables = {
        'RECIPIENT_EMAIL': extract_email(task_data),
        'EMAIL_SUBJECT': extract_subject(task_data),
        'EMAIL_BODY': task_data['content'],
        'ORIGINAL_TASK_FILE': task_data['filename'],
        'APPROVAL_REASON': task_data['approval_reason']
    }

    output_path = PENDING_APPROVAL_PATH / f"{task_data['filename']}"
    generator.generate(variables, output_path)
```

---

## 🔄 Workflow

### 1. Generate Approval

```bash
python scripts/generate_approval.py email \
    --to "client@example.com" \
    --subject "Invoice" \
    --body "Content..." \
    --output "AI_Employee_Vault/Pending_Approval/invoice.md"
```

**Result:** File created in `Pending_Approval/`

### 2. Human Reviews

User opens file, reviews:
- Email content
- Recipient
- Attachments
- Purpose

### 3. Approve or Reject

**Approve:**
```bash
mv AI_Employee_Vault/Pending_Approval/invoice.md AI_Employee_Vault/Approved/
```

**Reject:**
```bash
mv AI_Employee_Vault/Pending_Approval/invoice.md AI_Employee_Vault/Rejected/
```

### 4. Automatic Execution

Approval executor detects file in `Approved/` and:
1. Parses metadata
2. Executes via MCP
3. Logs result
4. Moves to Done/Failed

---

## 🔧 Customization

### Add Custom Fields

Edit template to add new fields:

```yaml
# In approval_email.md metadata section
custom_field: {{CUSTOM_VALUE}}
notification_email: {{NOTIFICATION_EMAIL}}
```

Then provide in variables:
```python
variables = {
    'CUSTOM_VALUE': 'my_value',
    'NOTIFICATION_EMAIL': 'notify@example.com'
}
```

### Conditional Content

Use conditional blocks:

```markdown
{{#if EMAIL_CC}}
**CC:** {{EMAIL_CC}}
{{/if}}

{{#if ATTACHMENTS}}
**Attachments:**
{{#each ATTACHMENTS}}
  - {{name}}
{{/each}}
{{/if}}
```

---

## 📊 Template Structure

### Metadata Section (YAML)
```yaml
---
action: send_email
mcp_server: gmail
mcp_tool: send_email
mcp_params:
  to: recipient@example.com
  subject: Subject
  body: Content
---
```

### Preview Section (Markdown)
```markdown
## Email Preview
[Human-readable preview]
```

### Approval Instructions
```markdown
## How to Approve
[Instructions for approving/rejecting]
```

### Technical Details
```markdown
## Technical Details
[MCP configuration, retry logic, etc.]
```

---

## ✅ Best Practices

### 1. Use Descriptive Filenames
```bash
# Good
send_invoice_to_client_acme_2026-02-05.md
draft_weekly_report_team_week_6.md

# Bad
email.md
action1.md
```

### 2. Include Context
```yaml
original_task: weekly_report_task.md
requires_approval_reason: "Email to external recipient"
```

### 3. Set Appropriate Expiry
```yaml
# Urgent
expires: 2026-02-05T18:00:00Z  # Same day

# Normal
expires: 2026-02-07T10:00:00Z  # 2 days

# Low priority
expires: 2026-02-10T10:00:00Z  # 5 days
```

### 4. Test First
```bash
# Always test with dry-run
python scripts/approval_executor.py --dry-run --once
```

---

## 🎓 Examples

See `examples/` directory for complete examples:
- `sample_email_action.md`
- `sample_draft_action.md`
- `sample_search_action.md`

---

## 📞 Support

- **Generator Script:** `scripts/generate_approval.py`
- **Executor Script:** `scripts/approval_executor.py`
- **Executor Guide:** `APPROVAL_EXECUTOR_GUIDE.md`
- **Technical README:** `scripts/APPROVAL_EXECUTOR_README.md`

---

**Last Updated:** February 2026
**Version:** 1.0.0
