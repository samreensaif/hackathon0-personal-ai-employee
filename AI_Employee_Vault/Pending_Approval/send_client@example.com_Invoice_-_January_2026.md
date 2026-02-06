---
action: send_email
mcp_server: gmail
mcp_tool: send_email
mcp_params:
  to: client@example.com
  subject: Invoice - January 2026
  body: |
    Dear Client, Please find attached the invoice for January 2026 services. Total: ,000. Thank you for your business.
  cc: []
  bcc: []
  attachments: []
requires_approval: true
approval_status: pending
created_at: 2026-02-05T17:25:20.413004
expires_at: 2026-02-06T17:25:20.413004
retry_config:
  max_retries: 3
  retry_delay: 60
  exponential_backoff: true
rate_limit:
  max_per_hour: 10
  current_count: 0
security_checklist:
  - recipient_verified: false
  - content_reviewed: false
  - attachments_scanned: false
  - compliance_checked: false
---

# Approval Request: Send Email

## Action Summary
**Type:** Send Email via Gmail MCP
**Recipient:** client@example.com
**Subject:** Invoice - January 2026
**Priority:** Medium
**Created:** 2026-02-05T17:25:20.413004
**Expires:** 2026-02-06T17:25:20.413004

## Email Preview

**To:** client@example.com


**Subject:** Invoice - January 2026

```
Dear Client, Please find attached the invoice for January 2026 services. Total: ,000. Thank you for your business.
```

**Attachments:** None

## Security Checklist

Before approving, please verify:
- [ ] Recipient email address is correct
- [ ] Email content is accurate and professional
- [ ] No sensitive information is exposed
- [ ] Attachments (if any) are correct
- [ ] Cc/Bcc recipients are appropriate
- [ ] Complies with company communication policy

## MCP Configuration

**Server:** gmail (mcp_servers/email/server.js)
**Tool:** send_email
**Rate Limit:** 0/10 emails this hour
**Timeout:** 30 seconds
**Retry:** 3 attempts with exponential backoff

## Approval Instructions

To approve this email:
```bash
# Option 1: Approve via approval executor
python scripts/approval_executor.py

# Option 2: Manually approve
# Edit this file and set: approval_status: approved
```

To reject:
```bash
# Set: approval_status: rejected
# Add: rejection_reason: "reason here"
```

## Risk Assessment

**Risk Level:** Medium
- External communication
- Represents company
- Client-facing

**Mitigation:**
- Human approval required
- Content review
- Rate limiting enforced
- Audit log maintained
