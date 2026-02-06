---
# =============================================================================
# APPROVAL REQUEST - EMAIL ACTION
# =============================================================================
#
# This file represents an action that requires human approval before execution.
# Once approved, move to AI_Employee_Vault/Approved/ for automatic execution.
#
# To approve: Review details below, then move to Approved/ folder
# To reject:  Move to Rejected/ folder with reason in rejection_reason field
#

# Basic Information
type: approval_request
action: send_email
priority: medium
created: 2026-02-05T10:30:00Z
expires: 2026-02-07T10:30:00Z
status: pending

# MCP Configuration
mcp_server: gmail
mcp_tool: send_email
mcp_params:
  to: {{RECIPIENT_EMAIL}}
  subject: {{EMAIL_SUBJECT}}
  cc: {{EMAIL_CC}}
  body: |
    {{EMAIL_BODY}}
  attachments:
    - path: {{ATTACHMENT_PATH_1}}
      name: {{ATTACHMENT_NAME_1}}
      mime_type: {{ATTACHMENT_MIME_TYPE_1}}

# Email-Specific Fields
email_to: {{RECIPIENT_EMAIL}}
email_subject: {{EMAIL_SUBJECT}}
email_cc: {{EMAIL_CC}}
email_body_preview: {{BODY_PREVIEW_100_CHARS}}

# Execution Configuration
retry_count: 0
max_retries: 3
timeout_seconds: 30
retry_delay_seconds: 2
retry_backoff_multiplier: 2

# Approval Metadata
approvedAt: null
approvedBy: null
rejectedAt: null
rejectedBy: null
rejection_reason: null

# Task Context
original_task: {{ORIGINAL_TASK_FILE}}
task_priority: {{TASK_PRIORITY}}
task_category: {{TASK_CATEGORY}}
requires_approval_reason: {{APPROVAL_REASON}}

---

# 📧 Email Approval Request

## ⚠️ Action Summary

**Type:** Send Email via Gmail
**Recipient:** {{RECIPIENT_EMAIL}}
**Subject:** {{EMAIL_SUBJECT}}
**Priority:** {{PRIORITY_LEVEL}}

---

## 📋 Email Preview

**From:** [Your Gmail Account]
**To:** {{RECIPIENT_EMAIL}}
{{#if EMAIL_CC}}
**CC:** {{EMAIL_CC}}
{{/if}}
**Subject:** {{EMAIL_SUBJECT}}
{{#if ATTACHMENTS}}
**Attachments:** {{ATTACHMENT_COUNT}} file(s)
{{#each ATTACHMENTS}}
  - {{name}} ({{size}})
{{/each}}
{{/if}}

---

## 📝 Email Content

{{EMAIL_BODY_FULL}}

---

## 🔍 Approval Checklist

Review the following before approving:

- [ ] Recipient email address is correct
- [ ] Subject line is appropriate
- [ ] Email content is accurate and professional
- [ ] No sensitive information is exposed
- [ ] Attachments are correct (if any)
- [ ] Tone and language are appropriate
- [ ] No typos or errors
- [ ] Action is necessary and timely

---

## ✅ How to Approve

1. **Review** the email content above carefully
2. **Verify** recipient and subject are correct
3. **Check** that all information is accurate
4. **Move this file** to `AI_Employee_Vault/Approved/`
5. The approval executor will automatically send the email

```bash
# Approve via command line
mv AI_Employee_Vault/Pending_Approval/{{FILE_NAME}} AI_Employee_Vault/Approved/
```

---

## ❌ How to Reject

1. **Move this file** to `AI_Employee_Vault/Rejected/`
2. **Add rejection reason** by editing the file:
   ```yaml
   rejection_reason: "Recipient email is incorrect"
   rejectedAt: 2026-02-05T11:30:00Z
   rejectedBy: user@example.com
   ```

```bash
# Reject via command line
mv AI_Employee_Vault/Pending_Approval/{{FILE_NAME}} AI_Employee_Vault/Rejected/
```

---

## 🔧 Technical Details

### MCP Server Configuration

**Server:** gmail (Node.js MCP server)
**Tool:** send_email
**Transport:** stdio
**Timeout:** 30 seconds

### Retry Logic

- **Max retries:** 3 attempts
- **Initial delay:** 2 seconds
- **Backoff:** Exponential (2s → 4s → 8s)
- **Total max time:** ~14 seconds

### Rate Limiting

- **Limit:** 10 actions per hour
- **Window:** Sliding 1-hour window
- **Current usage:** {{CURRENT_RATE_LIMIT_USAGE}}/10

### Error Handling

If execution fails:
- Retries automatically (up to 3 times)
- Logs detailed error to `Logs/YYYY-MM-DD.json`
- Moves file to `Failed/` folder
- Updates Dashboard.md with failure

---

## 📊 Context Information

### Original Task

**File:** {{ORIGINAL_TASK_FILE}}
**Priority:** {{TASK_PRIORITY}}
**Category:** {{TASK_CATEGORY}}
**Created:** {{TASK_CREATED_DATE}}

### Why Approval Required

{{APPROVAL_REASON}}

Examples:
- Contains payment/financial keywords
- Sends email to external recipient
- Contains sensitive information
- High-priority action

---

## ⏱️ Time Constraints

**Created:** {{CREATED_TIMESTAMP}}
**Expires:** {{EXPIRES_TIMESTAMP}}
**Time remaining:** {{TIME_REMAINING}}

⚠️ If not approved by expiry date, this action will be automatically rejected.

---

## 🔐 Security Review

Before approving, verify:

- [ ] **Recipient is trusted** - Verify email domain and recipient
- [ ] **Content is safe** - No sensitive data, credentials, or private info
- [ ] **Attachments are clean** - If included, verify file contents
- [ ] **Purpose is legitimate** - Action aligns with business needs
- [ ] **Timing is appropriate** - Not spam or excessive frequency

---

## 📝 Approval Log

This section is automatically updated when action is approved/rejected.

### Status History

- **{{CREATED_TIMESTAMP}}** - Created, pending approval
- **{{APPROVED_TIMESTAMP}}** - Approved by {{APPROVER}}
- **{{EXECUTED_TIMESTAMP}}** - Executed successfully / Failed ({{ERROR}})

---

## 🎯 Expected Outcome

After approval and execution:

1. ✉️ Email will be sent via Gmail API
2. 📋 File moved to `Done/` folder
3. 📊 Dashboard.md updated with success
4. 📝 Execution logged to `Logs/YYYY-MM-DD.json`
5. ✅ Task marked as completed

---

## 📞 Support

If you have questions about this approval request:

- **Check original task:** `AI_Employee_Vault/{{ORIGINAL_TASK_FILE}}`
- **View task history:** `AI_Employee_Vault/Logs/{{TASK_DATE}}.json`
- **Review dashboard:** `AI_Employee_Vault/Dashboard.md`

---

## 🚨 Important Notes

- **Expiry:** This request expires in {{TIME_REMAINING}}
- **Rate limit:** {{CURRENT_RATE_LIMIT_USAGE}}/10 actions used this hour
- **Retry:** Will retry up to 3 times if fails
- **Logging:** All actions are logged for audit trail

---

**Generated by:** AI Employee System (Silver Tier)
**Template version:** 1.0.0
**Last updated:** 2026-02-05
