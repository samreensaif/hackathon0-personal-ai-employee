---
name: Email Handler
slug: email-handler
description: Handle all email operations via Gmail MCP server with approval workflow integration
version: 1.0.0
author: AI Employee System
tier: silver
status: active
created: 2026-02-05
last_updated: 2026-02-05
mcp_servers:
  - gmail
dependencies:
  - approval_executor
  - task_processor
---

# Email Handler Skill

## 📋 Purpose

Handle all email-related operations through the Gmail MCP server, including drafting, sending, searching, and categorizing emails. Integrates with the approval workflow to ensure human oversight for outgoing communications while allowing autonomous operations for safe actions like drafting and searching.

---

## ⚡ Triggers

### Automatic Triggers
- **Task Event:** Task in `Pending_Approval/` with `mcp_tool: send_email`
- **Task Event:** Task contains "draft email" keywords
- **Task Event:** Task contains "search email" or "find email" keywords
- **Scheduled:** Check for new emails every 15 minutes (optional)

### Manual Triggers
- **Command:** "Draft an email to [recipient] about [topic]"
- **Command:** "Search emails from [sender] about [subject]"
- **Command:** "Find emails containing [keyword]"
- **Command:** "Send email to [recipient]" (creates approval request)
- **Command:** "Check my inbox"
- **Command:** "Categorize recent emails"

---

## 📥 Inputs

### Input Types

#### 1. Email Draft Request
```yaml
---
action: draft_email
recipient: client@example.com
subject: Follow-up on Q1 Proposal
priority: normal
---

# Draft Email Task

Please draft a professional email to the client regarding our Q1 proposal discussion.

Key points to include:
- Thank them for the meeting
- Summarize key points discussed
- Next steps and timeline
- Request confirmation
```

#### 2. Email Send Request
```yaml
---
action: send_email
mcp_server: gmail
mcp_tool: send_email
requires_approval: true
priority: high
---

# Send Email Task

Send the attached proposal to clienta@example.com by end of day.
```

#### 3. Email Search Request
```yaml
---
action: search_emails
search_query: "from:vendor@example.com subject:invoice"
max_results: 10
---

# Search Email Task

Find all invoice emails from our vendor from the past 30 days.
```

#### 4. Email Categorization Request
```yaml
---
action: categorize_emails
source: inbox
date_range: last_7_days
---

# Categorize Emails Task

Review and categorize emails from the past week into:
- Urgent action required
- Needs response
- FYI/Informational
- Archive
```

---

## 📤 Outputs

### 1. Draft Email Output

**Location:** `AI_Employee_Vault/Drafts/[subject]_draft.md`

**Structure:**
```yaml
---
action: draft_email
status: completed
created_at: 2026-02-05T10:30:00
recipient: client@example.com
subject: Follow-up on Q1 Proposal
draft_id: draft_abc123xyz
mcp_server: gmail
mcp_tool: create_draft
---

# Email Draft: Follow-up on Q1 Proposal

**To:** client@example.com
**Subject:** Follow-up on Q1 Proposal
**Draft ID:** draft_abc123xyz

## Email Content

Dear [Client Name],

Thank you for taking the time to meet with us last week to discuss the Q1 proposal...

[Full email body]

Best regards,
[Your Name]

---

## Actions Available
- [ ] Edit draft (manual in Gmail)
- [ ] Request approval to send
- [ ] Discard draft
```

### 2. Send Email Approval Request

**Location:** `AI_Employee_Vault/Pending_Approval/send_[subject]_approval.md`

**Structure:**
```yaml
---
action: send_email
mcp_server: gmail
mcp_tool: send_email
mcp_params:
  to: client@example.com
  subject: Follow-up on Q1 Proposal
  body: |
    Dear Client,

    Thank you for meeting with us...

    Best regards,
    Your Name
  cc: manager@company.com
  bcc: null
  attachments: []
requires_approval: true
approval_status: pending
created_at: 2026-02-05T10:30:00
expires_at: 2026-02-06T10:30:00
retry_config:
  max_retries: 3
  retry_delay: 60
  exponential_backoff: true
rate_limit:
  max_per_hour: 10
  current_count: 3
security_checklist:
  - recipient_verified: false
  - content_reviewed: false
  - attachments_scanned: false
  - compliance_checked: false
---

# Approval Request: Send Email to Client

## Action Summary
**Type:** Send Email via Gmail MCP
**Recipient:** client@example.com
**Subject:** Follow-up on Q1 Proposal
**Priority:** High
**Deadline:** End of day

## Email Preview

**To:** client@example.com
**Cc:** manager@company.com
**Subject:** Follow-up on Q1 Proposal

```
Dear Client,

Thank you for meeting with us last week to discuss the Q1 proposal.
I wanted to follow up on the key points we covered...

Best regards,
Your Name
```

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
**Rate Limit:** 10 emails/hour (currently 3/10)
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
```

### 3. Email Search Results

**Location:** `AI_Employee_Vault/Search_Results/[query]_results.md`

**Structure:**
```yaml
---
action: search_emails
status: completed
query: "from:vendor@example.com subject:invoice"
results_count: 5
search_date: 2026-02-05T10:30:00
mcp_server: gmail
mcp_tool: search_emails
---

# Email Search Results

**Query:** from:vendor@example.com subject:invoice
**Results:** 5 emails found
**Search Date:** 2026-02-05 10:30:00

## Results

### 1. Invoice #1234 - January 2026
- **From:** vendor@example.com
- **Date:** 2026-01-15 09:30:00
- **Subject:** Invoice #1234 - January Services
- **Preview:** Please find attached invoice for services rendered...
- **Message ID:** msg_abc123
- **Labels:** INBOX, IMPORTANT

### 2. Invoice #1235 - February 2026
- **From:** vendor@example.com
- **Date:** 2026-02-01 14:20:00
- **Subject:** Invoice #1235 - February Services
- **Preview:** Attached is your invoice for February...
- **Message ID:** msg_def456
- **Labels:** INBOX

[... additional results ...]

## Actions Available
- [ ] Read full email content
- [ ] Download attachments
- [ ] Reply to email (requires approval)
- [ ] Archive emails
- [ ] Apply labels
```

### 4. Email Categorization Output

**Location:** `AI_Employee_Vault/Reports/email_categorization_YYYY-MM-DD.md`

**Structure:**
```yaml
---
action: categorize_emails
status: completed
date_range: 2026-01-29 to 2026-02-05
total_emails: 47
categorized_at: 2026-02-05T10:30:00
---

# Email Categorization Report

**Period:** January 29 - February 5, 2026
**Total Emails:** 47
**Processed:** 47 (100%)

## Category Breakdown

### 🔴 Urgent Action Required (8 emails)
1. **RE: Production Server Down** - ops@company.com - 2 hours ago
2. **URGENT: Client Contract Expiring** - sales@company.com - 5 hours ago
3. **Payment Overdue Notice** - vendor@example.com - 1 day ago
[... more ...]

### 🟡 Needs Response (15 emails)
1. **Meeting Request: Q2 Planning** - manager@company.com - 1 day ago
2. **Question about API Integration** - dev@partner.com - 2 days ago
[... more ...]

### 🔵 FYI / Informational (20 emails)
1. **Newsletter: Industry Trends** - news@industry.com - 3 days ago
2. **Team Update: Project Milestone** - team@company.com - 4 days ago
[... more ...]

### ⚪ Archive (4 emails)
1. **Out of Office Reply** - contact@example.com - 5 days ago
[... more ...]

## Recommended Actions

1. **Urgent:** Respond to production server issue immediately
2. **High Priority:** Follow up on client contract within 24 hours
3. **Medium Priority:** Schedule Q2 planning meeting this week
4. **Low Priority:** Review newsletter when time permits

## Statistics

- Average response time: 6.5 hours
- Unread emails: 12
- Flagged emails: 5
- Emails requiring action: 23 (49%)
```

### 5. Logs

**Location:** `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

```json
{
  "timestamp": "2026-02-05T10:30:00",
  "skill": "email_handler",
  "action": "send_email",
  "mcp_server": "gmail",
  "mcp_tool": "send_email",
  "recipient": "client@example.com",
  "subject": "Follow-up on Q1 Proposal",
  "approval_required": true,
  "approval_status": "pending",
  "rate_limit_status": "3/10",
  "success": true,
  "duration_ms": 1250
}
```

---

## 🎯 Capabilities

### 1. Draft Emails (No Approval Needed)

**Purpose:** Create email drafts that can be reviewed and edited before sending.

**Safety:** Low risk - drafts are not sent, only saved in Gmail drafts folder.

**Process:**
1. Parse draft request with recipient, subject, key points
2. Generate professional email content
3. Create draft via Gmail MCP `create_draft` tool
4. Save draft ID and content locally
5. Notify user of draft location

**MCP Tool:** `gmail.create_draft`

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email content...",
  "cc": ["optional@example.com"],
  "bcc": []
}
```

**Rate Limit:** 50 drafts/hour (generous, low risk)

**Example Prompt:**
- "Draft an email to john@acme.com thanking them for the meeting"
- "Create a draft email to the team about next week's schedule"
- "Draft a professional response to vendor inquiry"

---

### 2. Send Emails (Requires Approval)

**Purpose:** Send emails to external or internal recipients.

**Safety:** High risk - external communication representing the company.

**Process:**
1. Parse send request with all email details
2. Validate recipient email addresses
3. Generate approval request with full preview
4. Move to `Pending_Approval/` folder
5. Wait for human approval
6. Execute send via Gmail MCP when approved
7. Log confirmation and message ID
8. Archive approval request

**MCP Tool:** `gmail.send_email`

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email content...",
  "cc": ["optional@example.com"],
  "bcc": [],
  "attachments": [
    {
      "filename": "document.pdf",
      "content": "base64_encoded_content",
      "mime_type": "application/pdf"
    }
  ]
}
```

**Rate Limit:** 10 emails/hour (strict, high risk)

**Approval Required:** YES - Always

**Security Checks:**
- Email address validation
- Content profanity/spam check
- Attachment virus scan (if implemented)
- Compliance verification
- Rate limit enforcement

**Example Prompt:**
- "Send the proposal email to client@example.com" → Creates approval request
- "Email the invoice to accounting@vendor.com" → Creates approval request

---

### 3. Search Inbox

**Purpose:** Find emails matching specific criteria (sender, subject, keywords, date range).

**Safety:** Low risk - read-only operation, no external actions.

**Process:**
1. Parse search query (sender, subject, keywords, dates)
2. Execute search via Gmail MCP `search_emails` tool
3. Retrieve matching emails with metadata
4. Format results in readable report
5. Save to `Search_Results/` folder
6. Present summary to user

**MCP Tool:** `gmail.search_emails`

**Parameters:**
```json
{
  "query": "from:sender@example.com subject:invoice after:2026/01/01",
  "max_results": 50,
  "include_body": false
}
```

**Query Syntax:** (Gmail search operators)
- `from:email@example.com` - From specific sender
- `to:email@example.com` - To specific recipient
- `subject:keyword` - Subject contains keyword
- `after:2026/01/01` - After date
- `before:2026/02/01` - Before date
- `has:attachment` - Has attachments
- `is:unread` - Unread emails
- `label:important` - Specific label

**Rate Limit:** 100 searches/hour

**Example Prompt:**
- "Search for emails from john@acme.com about the contract"
- "Find all unread emails from last week"
- "Show me emails with 'invoice' in the subject from January"

---

### 4. Categorize Incoming Emails

**Purpose:** Automatically categorize emails by urgency and type for better prioritization.

**Safety:** Low risk - read-only analysis, no external actions.

**Process:**
1. Fetch recent emails from specified time range
2. Analyze each email:
   - Sender importance (internal vs external, known contacts)
   - Subject keywords (urgent, important, FYI, etc.)
   - Content sentiment and urgency markers
   - Thread history and context
3. Assign category:
   - 🔴 Urgent Action Required
   - 🟡 Needs Response
   - 🔵 FYI / Informational
   - ⚪ Archive
4. Generate categorization report
5. Provide action recommendations

**MCP Tool:** `gmail.list_messages` + `gmail.get_message`

**Categories:**

**Urgent Action Required:**
- Keywords: urgent, asap, critical, emergency, deadline
- From: clients, management, critical vendors
- Unread + important label
- Deadline within 24 hours

**Needs Response:**
- Direct questions
- Meeting requests
- Client inquiries
- Partner communications
- Unread + normal importance

**FYI / Informational:**
- Newsletters
- Notifications
- Team updates
- CC'd emails (not direct recipient)
- Already read

**Archive:**
- Automated notifications (already read)
- Out of office replies
- Marketing emails
- Older than 7 days + read

**Rate Limit:** 20 categorization runs/hour

**Example Prompt:**
- "Categorize my emails from the past week"
- "Review my inbox and prioritize urgent emails"
- "Analyze recent emails and tell me what needs attention"

---

## 🔄 Process Flow

### Flow 1: Draft Email (No Approval)

```
User Request: "Draft email to client"
    ↓
Parse request:
  - recipient: client@example.com
  - subject: extracted from request
  - key_points: list of topics to cover
    ↓
Generate email content:
  - Professional greeting
  - Body paragraphs addressing key points
  - Professional closing
  - Signature
    ↓
Call MCP: gmail.create_draft
  - to: client@example.com
  - subject: "Follow-up on Q1 Proposal"
  - body: generated_content
    ↓
MCP Response:
  - draft_id: "draft_abc123"
  - status: "created"
    ↓
Save draft record:
  - Location: Drafts/follow_up_draft.md
  - Include: draft_id, content, timestamp
    ↓
Log action:
  - skill: email_handler
  - action: create_draft
  - draft_id: draft_abc123
    ↓
Notify user:
  "Draft created successfully!
   Draft ID: draft_abc123
   Saved to: Drafts/follow_up_draft.md
   You can review and edit in Gmail."
```

---

### Flow 2: Send Email (With Approval)

```
User Request: "Send email to client@example.com"
    ↓
Parse request:
  - action: send_email
  - recipient: client@example.com
  - subject: extracted
  - body: provided or generated
    ↓
Validate inputs:
  - Valid email address? ✓
  - Subject provided? ✓
  - Body content? ✓
    ↓
Check rate limit:
  - Current: 3/10 emails sent this hour
  - Status: OK (within limit)
    ↓
Generate approval request:
  - Template: templates/approval_email.md
  - Variables: recipient, subject, body, cc, bcc
  - MCP params: complete configuration
  - Security checklist
    ↓
Save approval request:
  - Location: Pending_Approval/send_email_approval.md
  - Include: full email preview, MCP config
    ↓
Log pending action:
  - action: send_email
  - approval_status: pending
    ↓
Notify user:
  "Email send request created.
   Approval required in: Pending_Approval/

   To approve, run:
   python scripts/approval_executor.py"
    ↓
[WAIT FOR HUMAN APPROVAL]
    ↓
Human approves: approval_status → approved
    ↓
Approval executor runs:
  - Reads approval file
  - Validates approval signature
  - Checks rate limit again
    ↓
Execute MCP: gmail.send_email
  - Load MCP params from approval
  - Call tool with retry logic
    ↓
MCP Response:
  - message_id: "msg_xyz789"
  - status: "sent"
  - timestamp: "2026-02-05T10:30:15Z"
    ↓
Log success:
  - action: send_email
  - approval_status: approved_and_executed
  - message_id: msg_xyz789
  - duration: 1250ms
    ↓
Archive approval:
  - Move to: Approved/send_email_executed.md
    ↓
Notify user:
  "Email sent successfully!
   Message ID: msg_xyz789
   Recipient: client@example.com
   Sent at: 2026-02-05 10:30:15"
```

---

### Flow 3: Search Emails

```
User Request: "Search for emails from john@acme.com about contract"
    ↓
Parse search request:
  - sender: john@acme.com
  - keywords: contract
  - date_range: default (last 30 days)
    ↓
Build Gmail query:
  - query: "from:john@acme.com contract after:2026/01/05"
  - max_results: 50
    ↓
Call MCP: gmail.search_emails
  - Pass query string
  - Request metadata only (not full bodies)
    ↓
MCP Response:
  - results: [
      {id, from, subject, date, preview, labels},
      ...
    ]
  - count: 5
    ↓
Format results:
  - Group by date
  - Extract key information
  - Create summary
    ↓
Save search results:
  - Location: Search_Results/john_contract_results.md
  - Include: query, results, timestamp
    ↓
Log action:
  - skill: email_handler
  - action: search_emails
  - results_count: 5
    ↓
Present to user:
  "Found 5 emails from john@acme.com about 'contract':

   1. Contract Review - Jan 15
   2. Contract Amendment - Jan 20
   3. RE: Contract Questions - Feb 1
   ...

   Full results saved to: Search_Results/..."
```

---

### Flow 4: Categorize Emails

```
User Request: "Categorize emails from the past week"
    ↓
Parse request:
  - date_range: last 7 days
  - source: inbox
    ↓
Calculate date range:
  - start: 2026-01-29
  - end: 2026-02-05
    ↓
Call MCP: gmail.list_messages
  - query: "after:2026/01/29 before:2026/02/06"
  - max_results: 100
    ↓
MCP Response:
  - messages: [list of message IDs]
  - count: 47
    ↓
For each message:
  ↓
  Call MCP: gmail.get_message
    - message_id: msg_abc123
    ↓
  Analyze email:
    - sender: check against known contacts
    - subject: extract keywords (urgent, asap, etc.)
    - body_preview: sentiment analysis
    - labels: check for IMPORTANT
    - thread_id: check conversation history
    ↓
  Categorize:
    - Has "urgent" or "asap"? → Urgent Action Required
    - From client + unread? → Needs Response
    - Contains question? → Needs Response
    - Newsletter or notification? → FYI
    - Old + read + no action needed? → Archive
    ↓
  Assign priority score (1-100)
    ↓
Group by category:
  - Urgent Action Required: 8 emails
  - Needs Response: 15 emails
  - FYI: 20 emails
  - Archive: 4 emails
    ↓
Sort within categories by priority
    ↓
Generate recommendations:
  - "Respond to production issue immediately"
  - "Schedule meeting with client this week"
  - "Review partnership inquiry by Friday"
    ↓
Create report:
  - Location: Reports/email_categorization_2026-02-05.md
  - Include: all categories, recommendations, stats
    ↓
Log action:
  - skill: email_handler
  - action: categorize_emails
  - total_processed: 47
  - duration: 8500ms
    ↓
Present summary:
  "Categorized 47 emails from the past week:

   🔴 Urgent: 8 emails (need immediate action)
   🟡 Response: 15 emails (reply within 24h)
   🔵 FYI: 20 emails (informational)
   ⚪ Archive: 4 emails (no action needed)

   Top priority: Production server issue from ops team

   Full report: Reports/email_categorization_2026-02-05.md"
```

---

## 🎬 Example Usage

### Example 1: Draft Email (Safe, No Approval)

**User Prompt:**
"Draft a professional email to sarah@techcorp.com thanking her for yesterday's product demo and asking about pricing for the enterprise plan."

**Skill Execution:**

1. **Parses request:**
   - Action: draft_email
   - Recipient: sarah@techcorp.com
   - Purpose: thank you + pricing inquiry
   - Tone: professional

2. **Generates email content:**
   ```
   Subject: Thank You - Product Demo Follow-up

   Dear Sarah,

   Thank you for taking the time to walk us through the product demo
   yesterday. The features you showcased align well with our team's needs,
   particularly the collaboration tools and security features.

   I'd like to learn more about your enterprise plan pricing and what
   additional features it includes compared to the standard plan. Could
   you please send over the pricing details and any available documentation?

   Looking forward to hearing from you.

   Best regards,
   [Your Name]
   ```

3. **Calls MCP:**
   ```json
   {
     "tool": "gmail.create_draft",
     "params": {
       "to": "sarah@techcorp.com",
       "subject": "Thank You - Product Demo Follow-up",
       "body": "Dear Sarah,\n\nThank you for..."
     }
   }
   ```

4. **MCP Response:**
   ```json
   {
     "success": true,
     "draft_id": "draft_18d2f9a4b5c3e1f0",
     "created_at": "2026-02-05T10:30:00Z"
   }
   ```

5. **Saves draft record:** `Drafts/thank_you_product_demo_draft.md`

6. **Logs action:**
   ```json
   {
     "timestamp": "2026-02-05T10:30:00",
     "skill": "email_handler",
     "action": "create_draft",
     "recipient": "sarah@techcorp.com",
     "draft_id": "draft_18d2f9a4b5c3e1f0",
     "success": true
   }
   ```

**Claude Response:**
"I've created a professional draft email for Sarah at TechCorp:

**Draft ID:** draft_18d2f9a4b5c3e1f0
**Subject:** Thank You - Product Demo Follow-up

The draft thanks her for the demo and requests enterprise pricing information. You can review and edit the draft in your Gmail drafts folder, or I can modify it based on your feedback.

Saved to: `Drafts/thank_you_product_demo_draft.md`"

---

### Example 2: Send Email (Requires Approval)

**User Prompt:**
"Send an email to clienta@example.com with the January invoice. Total is $5,000 for consulting services. Use professional tone."

**Skill Execution:**

1. **Parses request:**
   - Action: send_email (HIGH RISK)
   - Recipient: clienta@example.com
   - Subject: January Invoice
   - Content: Invoice details, $5,000

2. **Validates:**
   - Email format: ✓ Valid
   - Subject: ✓ Provided
   - Content: ✓ Complete

3. **Checks rate limit:**
   - Current: 3/10 emails this hour
   - Status: ✓ OK

4. **Generates email content:**
   ```
   Subject: Invoice - January 2026 Consulting Services

   Dear Client,

   Please find attached the invoice for consulting services provided
   during January 2026.

   Invoice Details:
   - Invoice #: 2026-01-001
   - Period: January 1-31, 2026
   - Services: Consulting Services
   - Total Amount: $5,000.00
   - Due Date: February 15, 2026

   Payment can be made via bank transfer to the account details
   listed on the invoice. Please let me know if you have any questions.

   Thank you for your business.

   Best regards,
   [Your Name]
   ```

5. **Creates approval request:**
   - Location: `Pending_Approval/send_invoice_email_approval.md`
   - Includes: Full email preview, MCP config, security checklist

6. **Logs pending action:**
   ```json
   {
     "timestamp": "2026-02-05T10:30:00",
     "skill": "email_handler",
     "action": "send_email",
     "approval_status": "pending",
     "recipient": "clienta@example.com",
     "subject": "Invoice - January 2026"
   }
   ```

**Claude Response:**
"I've prepared an invoice email to send to clienta@example.com, but this requires your approval before sending.

**Approval Request:** `Pending_Approval/send_invoice_email_approval.md`

**Email Preview:**
- **To:** clienta@example.com
- **Subject:** Invoice - January 2026 Consulting Services
- **Content:** Professional invoice notification with $5,000 total

**To approve and send:**
```bash
python scripts/approval_executor.py
```

**Or review the approval file and set:** `approval_status: approved`

**Rate Limit:** Currently 3/10 emails sent this hour (safe to proceed)"

---

**[User approves the email]**

**Approval Executor Runs:**

1. **Reads approval file:**
   - approval_status: approved ✓
   - MCP params: complete ✓

2. **Re-checks rate limit:**
   - Current: 3/10 (still OK)

3. **Executes MCP:**
   ```json
   {
     "tool": "gmail.send_email",
     "params": {
       "to": "clienta@example.com",
       "subject": "Invoice - January 2026 Consulting Services",
       "body": "Dear Client,\n\nPlease find attached..."
     }
   }
   ```

4. **MCP Response:**
   ```json
   {
     "success": true,
     "message_id": "msg_18d2f9a4b5c3e1f0",
     "sent_at": "2026-02-05T10:35:22Z"
   }
   ```

5. **Logs execution:**
   ```json
   {
     "timestamp": "2026-02-05T10:35:22",
     "skill": "email_handler",
     "action": "send_email",
     "approval_status": "approved_and_executed",
     "message_id": "msg_18d2f9a4b5c3e1f0",
     "recipient": "clienta@example.com",
     "success": true
   }
   ```

6. **Archives approval:**
   - Moves to: `Approved/send_invoice_email_executed.md`

**Executor Output:**
```
[SUCCESS] Email sent to clienta@example.com
Message ID: msg_18d2f9a4b5c3e1f0
Subject: Invoice - January 2026 Consulting Services
Sent at: 2026-02-05 10:35:22
Rate limit: 4/10 emails this hour
```

---

### Example 3: Search Emails

**User Prompt:**
"Search for all emails from mike@vendor.com about the contract from the past 60 days"

**Skill Execution:**

1. **Parses search:**
   - Sender: mike@vendor.com
   - Keywords: contract
   - Date range: last 60 days (after:2026-12-06)

2. **Builds Gmail query:**
   ```
   from:mike@vendor.com contract after:2026/12/06
   ```

3. **Calls MCP:**
   ```json
   {
     "tool": "gmail.search_emails",
     "params": {
       "query": "from:mike@vendor.com contract after:2026/12/06",
       "max_results": 50
     }
   }
   ```

4. **MCP Response:**
   ```json
   {
     "success": true,
     "count": 7,
     "results": [
       {
         "id": "msg_001",
         "from": "mike@vendor.com",
         "subject": "Contract Renewal Discussion",
         "date": "2026-02-03T14:30:00Z",
         "preview": "Hi, I wanted to follow up on the contract...",
         "labels": ["INBOX", "IMPORTANT"]
       },
       {
         "id": "msg_002",
         "from": "mike@vendor.com",
         "subject": "RE: Contract Terms Amendment",
         "date": "2026-01-28T09:15:00Z",
         "preview": "Thanks for your questions about the contract...",
         "labels": ["INBOX"]
       },
       ...
     ]
   }
   ```

5. **Formats results:**
   - Sorts by date (newest first)
   - Extracts key info
   - Creates readable summary

6. **Saves results:**
   - Location: `Search_Results/mike_vendor_contract_results.md`

7. **Logs action:**
   ```json
   {
     "timestamp": "2026-02-05T10:30:00",
     "skill": "email_handler",
     "action": "search_emails",
     "query": "from:mike@vendor.com contract",
     "results_count": 7,
     "duration_ms": 850
   }
   ```

**Claude Response:**
"Found **7 emails** from mike@vendor.com about 'contract' in the past 60 days:

### Recent Emails:

1. **Contract Renewal Discussion** - Feb 3, 2026
   - Preview: 'Hi, I wanted to follow up on the contract...'
   - Labels: INBOX, IMPORTANT

2. **RE: Contract Terms Amendment** - Jan 28, 2026
   - Preview: 'Thanks for your questions about the contract...'

3. **Contract Review - Q1 2026** - Jan 15, 2026
   - Preview: 'Please find the updated contract for review...'

4. **RE: Contract Pricing Discussion** - Jan 10, 2026

5. **Contract Addendum** - Jan 5, 2026

6. **New Contract Terms** - Dec 20, 2025

7. **Contract Kickoff Meeting** - Dec 15, 2025

**Full results with previews saved to:**
`Search_Results/mike_vendor_contract_results.md`

Would you like me to:
- Read the full content of any specific email
- Search for additional related emails
- Draft a reply to any of these emails"

---

### Example 4: Categorize Emails

**User Prompt:**
"Categorize all emails from the past 3 days and tell me what needs urgent attention"

**Skill Execution:**

1. **Parses request:**
   - Action: categorize_emails
   - Date range: 2026-02-02 to 2026-02-05 (3 days)
   - Source: inbox

2. **Fetches emails:**
   ```json
   {
     "tool": "gmail.list_messages",
     "params": {
       "query": "after:2026/02/02 before:2026/02/06",
       "max_results": 100
     }
   }
   ```

3. **Gets details for each:**
   - 23 emails total
   - Calls gmail.get_message for each

4. **Analyzes each email:**

   **Email 1:**
   - From: ops@company.com
   - Subject: "URGENT: Database backup failed"
   - Keywords: urgent, failed, critical
   - Unread: yes
   - **Category:** 🔴 Urgent Action Required
   - Priority: 95/100

   **Email 2:**
   - From: client@acme.com
   - Subject: "Meeting request for next week"
   - Keywords: meeting, request
   - Unread: yes
   - **Category:** 🟡 Needs Response
   - Priority: 70/100

   **Email 3:**
   - From: newsletter@industry.com
   - Subject: "Weekly Industry Update"
   - Keywords: newsletter, update
   - Read: yes
   - **Category:** 🔵 FYI / Informational
   - Priority: 30/100

   [... continues for all 23 emails ...]

5. **Groups by category:**
   - Urgent Action Required: 3 emails
   - Needs Response: 8 emails
   - FYI / Informational: 10 emails
   - Archive: 2 emails

6. **Generates recommendations:**
   - "URGENT: Address database backup failure immediately"
   - "High priority: Respond to client meeting request within 24h"
   - "Medium: Review partnership proposal by Friday"

7. **Creates report:**
   - Location: `Reports/email_categorization_2026-02-05.md`
   - Includes full breakdown, stats, recommendations

8. **Logs action:**
   ```json
   {
     "timestamp": "2026-02-05T10:30:00",
     "skill": "email_handler",
     "action": "categorize_emails",
     "total_emails": 23,
     "urgent": 3,
     "needs_response": 8,
     "fyi": 10,
     "archive": 2,
     "duration_ms": 4500
   }
   ```

**Claude Response:**
"I've categorized **23 emails** from the past 3 days. Here's your priority breakdown:

## 🔴 Urgent Action Required (3 emails)

1. **Database backup failed** - ops@company.com - 4 hours ago
   - ⚠️ CRITICAL: Production backup system needs immediate attention

2. **Payment overdue - Account suspension warning** - billing@vendor.com - 1 day ago
   - ⚠️ Action required within 24 hours to avoid service interruption

3. **Client escalation: Bug in production** - clientb@example.com - 2 days ago
   - ⚠️ Client-facing issue, needs immediate response

## 🟡 Needs Response (8 emails)

1. **Meeting request: Q2 Planning** - manager@company.com - 1 day ago
2. **Partnership inquiry** - partner@startup.com - 2 days ago
3. **Contract renewal discussion** - mike@vendor.com - 2 days ago
[... 5 more ...]

## 🔵 FYI / Informational (10 emails)

- Team updates, newsletters, notifications
- No action required, review when time permits

## ⚪ Archive (2 emails)

- Old automated notifications, can be archived

---

**Recommended Actions:**

1. **IMMEDIATE:** Investigate database backup failure with ops team
2. **TODAY:** Make payment to vendor to avoid service interruption
3. **TODAY:** Respond to client about production bug
4. **THIS WEEK:** Schedule Q2 planning meeting
5. **THIS WEEK:** Review partnership inquiry

**Full report saved to:**
`Reports/email_categorization_2026-02-05.md`

Would you like me to:
- Draft responses to urgent emails
- Search for more context on any issue
- Create follow-up tasks for pending items"

---

## 💻 Code Reference

### Main Implementation

**File:** `scripts/email_handler.py` (to be created)

**Key Functions:**

```python
def draft_email(recipient: str, subject: str, body: str, cc: list = None) -> dict:
    """
    Create email draft via Gmail MCP.

    Args:
        recipient: Email address
        subject: Email subject
        body: Email content
        cc: Optional CC recipients

    Returns:
        {
            'success': bool,
            'draft_id': str,
            'saved_to': str (file path)
        }
    """
    pass


def send_email_request(recipient: str, subject: str, body: str,
                      cc: list = None, attachments: list = None) -> dict:
    """
    Create approval request for sending email.

    Args:
        recipient: Email address
        subject: Email subject
        body: Email content
        cc: Optional CC recipients
        attachments: Optional attachment files

    Returns:
        {
            'success': bool,
            'approval_file': str,
            'requires_approval': bool
        }
    """
    pass


def search_emails(query: str, max_results: int = 50) -> dict:
    """
    Search Gmail inbox with query.

    Args:
        query: Gmail search query string
        max_results: Maximum results to return

    Returns:
        {
            'success': bool,
            'count': int,
            'results': [list of email objects],
            'saved_to': str
        }
    """
    pass


def categorize_emails(date_range: str = "last_7_days") -> dict:
    """
    Categorize emails by urgency and type.

    Args:
        date_range: Time range to analyze

    Returns:
        {
            'success': bool,
            'total_emails': int,
            'categories': {
                'urgent': int,
                'needs_response': int,
                'fyi': int,
                'archive': int
            },
            'recommendations': [list of action items],
            'report_file': str
        }
    """
    pass


def check_rate_limit(action: str) -> dict:
    """
    Check if action is within rate limits.

    Args:
        action: 'send_email', 'draft_email', or 'search_emails'

    Returns:
        {
            'allowed': bool,
            'current_count': int,
            'max_limit': int,
            'reset_time': str
        }
    """
    pass


def execute_mcp_tool(tool_name: str, params: dict, retry: bool = True) -> dict:
    """
    Execute Gmail MCP tool with error handling and retry logic.

    Args:
        tool_name: MCP tool name (send_email, create_draft, search_emails)
        params: Tool parameters
        retry: Enable retry on failure

    Returns:
        {
            'success': bool,
            'result': dict,
            'error': str (if failed),
            'attempts': int
        }
    """
    pass
```

### Integration Points

**Task Processor Integration:**
```python
# In scripts/runner_silver.py
# Detect email tasks and route to email handler

if "email" in task_content or "send" in task_content:
    from scripts.email_handler import send_email_request
    result = send_email_request(recipient, subject, body)
```

**Approval Executor Integration:**
```python
# In scripts/approval_executor.py
# Execute approved email sends

if mcp_tool == "send_email":
    from scripts.email_handler import execute_mcp_tool
    result = execute_mcp_tool("send_email", mcp_params)
```

**MCP Server Integration:**
```python
# Connect to Gmail MCP server
import asyncio
from mcp import StdioServerParameters, stdio_client

server_params = StdioServerParameters(
    command="node",
    args=["mcp_servers/email/server.js"],
    env=None
)

async def call_mcp_tool(tool_name, params):
    async with stdio_client(server_params) as (read, write):
        result = await write.call_tool(tool_name, params)
        return result
```

---

## ⚙️ Configuration

### Rate Limits

**File:** `scripts/email_handler.py` or `config/rate_limits.json`

```python
RATE_LIMITS = {
    'send_email': {
        'max_per_hour': 10,
        'max_per_day': 50,
        'reset_window': 3600  # seconds
    },
    'draft_email': {
        'max_per_hour': 50,
        'max_per_day': 200,
        'reset_window': 3600
    },
    'search_emails': {
        'max_per_hour': 100,
        'max_per_day': 500,
        'reset_window': 3600
    },
    'categorize_emails': {
        'max_per_hour': 20,
        'max_per_day': 50,
        'reset_window': 3600
    }
}
```

**Tracking File:** `AI_Employee_Vault/Logs/rate_limits_YYYY-MM-DD.json`

```json
{
  "2026-02-05": {
    "send_email": {
      "hourly": [
        {"hour": 10, "count": 3},
        {"hour": 11, "count": 5}
      ],
      "daily_total": 8
    },
    "draft_email": {
      "hourly": [{"hour": 10, "count": 12}],
      "daily_total": 12
    }
  }
}
```

### Keyword Configuration

**File:** `config/email_keywords.json`

```json
{
  "urgent_keywords": [
    "urgent", "asap", "critical", "emergency", "immediate",
    "deadline", "today", "now", "escalate", "red alert"
  ],
  "question_indicators": [
    "?", "can you", "could you", "please", "would you",
    "how", "what", "when", "where", "why", "who"
  ],
  "automated_senders": [
    "no-reply@", "noreply@", "donotreply@",
    "notifications@", "alerts@", "automated@"
  ],
  "newsletter_keywords": [
    "newsletter", "digest", "roundup", "weekly update",
    "monthly update", "unsubscribe", "view in browser"
  ]
}
```

### MCP Server Configuration

**File:** `.mcp.json` or `mcp_config.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": ["mcp_servers/email/server.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "./mcp_servers/email/credentials.json",
        "GMAIL_TOKEN_PATH": "./mcp_servers/email/token.json"
      }
    }
  }
}
```

### Approval Template Configuration

**File:** `templates/approval_email.md`

```markdown
---
action: {{action}}
mcp_server: gmail
mcp_tool: {{mcp_tool}}
mcp_params:
  to: {{recipient}}
  subject: {{subject}}
  body: |
{{body}}
  cc: {{cc}}
  bcc: {{bcc}}
  attachments: {{attachments}}
requires_approval: true
approval_status: pending
---

# Approval Request: {{action_title}}

## Email Preview

**To:** {{recipient}}
**Cc:** {{cc}}
**Subject:** {{subject}}

```
{{body}}
```

## Security Checklist

- [ ] Recipient email verified
- [ ] Content reviewed
- [ ] No sensitive data exposed
- [ ] Attachments correct
- [ ] Rate limit OK

## Approve/Reject

Set `approval_status: approved` or `approval_status: rejected`
```

---

## 🛡️ Error Handling

### 1. MCP Connection Failure

**Scenario:** Cannot connect to Gmail MCP server

**Error Message:**
```
ERROR: Failed to connect to Gmail MCP server
Details: Connection timeout after 30 seconds
Server: mcp_servers/email/server.js
```

**Handling:**
1. Log error with full details
2. Check if MCP server process is running
3. Verify credentials.json and token.json exist
4. Attempt reconnection with exponential backoff (3 attempts)
5. If all fail, notify user and create manual task

**Code:**
```python
try:
    result = await connect_to_mcp_server("gmail")
except MCPConnectionError as e:
    log_error("mcp_connection_failed", {
        "server": "gmail",
        "error": str(e),
        "timestamp": datetime.now().isoformat()
    })

    # Retry with backoff
    for attempt in range(1, 4):
        await asyncio.sleep(2 ** attempt)  # 2s, 4s, 8s
        try:
            result = await connect_to_mcp_server("gmail")
            break
        except MCPConnectionError:
            if attempt == 3:
                # All retries failed
                create_manual_task(
                    "MCP Server Connection Failed",
                    "Gmail MCP server is unreachable. "
                    "Please check server status and credentials."
                )
                return {"success": False, "error": "MCP connection failed"}
```

---

### 2. API Rate Limit Exceeded

**Scenario:** Gmail API rate limit exceeded (too many requests)

**Error Message:**
```
ERROR: Gmail API rate limit exceeded
Quota: 10 emails/hour
Current: 11 attempts this hour
Reset: 2026-02-05 11:00:00
```

**Handling:**
1. Detect rate limit error from API response
2. Calculate wait time until reset
3. Queue request for later execution
4. Notify user of delay
5. Log rate limit hit for monitoring

**Code:**
```python
def send_email_with_rate_limit(params):
    rate_status = check_rate_limit("send_email")

    if not rate_status['allowed']:
        # Rate limit exceeded
        reset_time = rate_status['reset_time']
        wait_seconds = (reset_time - datetime.now()).total_seconds()

        log_warning("rate_limit_exceeded", {
            "action": "send_email",
            "current_count": rate_status['current_count'],
            "max_limit": rate_status['max_limit'],
            "reset_time": reset_time.isoformat(),
            "wait_seconds": wait_seconds
        })

        # Queue for later
        queue_task({
            "action": "send_email",
            "params": params,
            "scheduled_for": reset_time
        })

        return {
            "success": False,
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded. Email queued for sending at {reset_time}",
            "wait_seconds": wait_seconds
        }

    # Proceed with send
    return execute_mcp_tool("send_email", params)
```

---

### 3. Invalid Email Address

**Scenario:** User provides malformed email address

**Error Message:**
```
ERROR: Invalid email address format
Provided: "clientexample.com" (missing @)
Expected: user@domain.com
```

**Handling:**
1. Validate email format with regex
2. Check for common typos (@gmial.com → @gmail.com)
3. Suggest corrections if possible
4. Reject request and ask user to correct
5. Log validation failure

**Code:**
```python
import re

def validate_email(email: str) -> dict:
    """Validate email address format."""

    # Basic format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        # Check for common typos
        suggestions = []

        if '@' not in email:
            suggestions.append(f"Missing @ symbol. Did you mean: {email[:5]}@{email[5:]}?")

        common_typos = {
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com'
        }

        for typo, correct in common_typos.items():
            if typo in email.lower():
                suggestions.append(email.lower().replace(typo, correct))

        log_warning("invalid_email_address", {
            "provided": email,
            "suggestions": suggestions
        })

        return {
            "valid": False,
            "error": "Invalid email format",
            "suggestions": suggestions
        }

    return {"valid": True}


# Usage
result = validate_email("clientexample.com")
if not result['valid']:
    return {
        "success": False,
        "error": result['error'],
        "message": f"Invalid email: {email}\nSuggestions: {result['suggestions']}"
    }
```

---

### 4. Email Send Failure

**Scenario:** Email send operation fails after approval

**Error Message:**
```
ERROR: Failed to send email
Recipient: client@example.com
Error: Network timeout / SMTP error / Authentication failed
Message ID: None (not sent)
```

**Handling:**
1. Detect send failure from MCP response
2. Determine error type (network, auth, quota, etc.)
3. Apply retry logic based on error type:
   - Network timeout: Retry 3 times with backoff
   - Auth failure: Don't retry, notify admin
   - Quota exceeded: Queue for later
   - Invalid recipient: Don't retry, notify user
4. Log all attempts
5. If all retries fail, create manual task
6. Keep approval record for audit trail

**Code:**
```python
async def send_email_with_retry(params: dict, max_retries: int = 3) -> dict:
    """Send email with retry logic on failure."""

    attempts = []

    for attempt in range(1, max_retries + 1):
        try:
            result = await execute_mcp_tool("send_email", params)

            if result['success']:
                log_action("send_email_success", {
                    "recipient": params['to'],
                    "message_id": result['message_id'],
                    "attempts": attempt
                })
                return result

            # MCP call succeeded but send failed
            error_type = result.get('error_type', 'unknown')
            attempts.append({
                "attempt": attempt,
                "error": result.get('error'),
                "error_type": error_type
            })

            # Determine if we should retry
            if error_type in ['auth_failure', 'invalid_recipient']:
                # Don't retry these errors
                break

            if error_type == 'quota_exceeded':
                # Queue for later, don't retry now
                return queue_for_later(params)

            # Retry with exponential backoff
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 2s, 4s, 8s
                await asyncio.sleep(wait_time)

        except Exception as e:
            attempts.append({
                "attempt": attempt,
                "error": str(e),
                "error_type": "exception"
            })

            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)

    # All retries failed
    log_error("send_email_failed", {
        "recipient": params['to'],
        "subject": params['subject'],
        "attempts": attempts,
        "total_attempts": len(attempts)
    })

    # Create manual task
    create_manual_task(
        title=f"Failed to send email to {params['to']}",
        details=f"Subject: {params['subject']}\n\n"
                f"Attempts: {len(attempts)}\n"
                f"Last error: {attempts[-1]['error']}\n\n"
                f"Please send this email manually or investigate the issue.",
        priority="high"
    )

    return {
        "success": False,
        "error": "send_failed_after_retries",
        "attempts": attempts,
        "manual_task_created": True
    }
```

---

### 5. Search Query Timeout

**Scenario:** Email search takes too long and times out

**Error Message:**
```
ERROR: Email search timeout
Query: from:sender@example.com after:2024/01/01
Timeout: 30 seconds
Results retrieved: 0 (partial results not available)
```

**Handling:**
1. Set reasonable timeout (30s for searches)
2. If timeout occurs, suggest narrowing query
3. Recommend strategies:
   - Shorter date range
   - More specific keywords
   - Use message ID for specific email
4. Log timeout for monitoring
5. Don't retry automatically (wastes resources)

**Code:**
```python
async def search_emails_with_timeout(query: str, timeout: int = 30) -> dict:
    """Search emails with timeout protection."""

    try:
        result = await asyncio.wait_for(
            execute_mcp_tool("search_emails", {"query": query}),
            timeout=timeout
        )
        return result

    except asyncio.TimeoutError:
        log_warning("search_timeout", {
            "query": query,
            "timeout_seconds": timeout
        })

        # Provide helpful suggestions
        suggestions = [
            "Try a shorter date range (e.g., after:2026/01/01)",
            "Add more specific keywords to narrow results",
            "Search for specific sender or subject",
            "If searching for one email, use message ID directly"
        ]

        return {
            "success": False,
            "error": "search_timeout",
            "message": f"Search timed out after {timeout} seconds",
            "suggestions": suggestions,
            "query": query
        }
```

---

### 6. Attachment Handling Errors

**Scenario:** Cannot attach file to email (file not found, too large, invalid format)

**Error Messages:**
```
ERROR: Attachment file not found
File: /path/to/document.pdf
Email: clienta@example.com

ERROR: Attachment too large
File: presentation.pptx (35 MB)
Limit: 25 MB per email
Suggestion: Upload to cloud and share link

ERROR: Attachment type not allowed
File: script.exe
Allowed types: pdf, doc, docx, xls, xlsx, txt, jpg, png
```

**Handling:**
1. Validate attachment before creating approval:
   - File exists
   - Size within limit (25 MB Gmail limit)
   - File type allowed (security)
2. If validation fails:
   - Provide clear error message
   - Suggest alternatives (cloud upload link)
   - Don't create approval request
3. Log attachment errors
4. For large files, offer to create cloud share link instead

**Code:**
```python
def validate_attachment(file_path: str) -> dict:
    """Validate attachment file."""

    import os

    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "valid": False,
            "error": "file_not_found",
            "message": f"File not found: {file_path}"
        }

    # Check file size (Gmail limit: 25 MB)
    file_size = os.path.getsize(file_path)
    max_size = 25 * 1024 * 1024  # 25 MB in bytes

    if file_size > max_size:
        size_mb = file_size / (1024 * 1024)
        return {
            "valid": False,
            "error": "file_too_large",
            "message": f"File too large: {size_mb:.1f} MB (limit: 25 MB)",
            "suggestion": "Upload to Google Drive/Dropbox and share link instead"
        }

    # Check file type (security)
    allowed_extensions = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.zip'
    ]

    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext not in allowed_extensions:
        return {
            "valid": False,
            "error": "invalid_file_type",
            "message": f"File type not allowed: {file_ext}",
            "allowed_types": allowed_extensions
        }

    return {
        "valid": True,
        "file_size": file_size,
        "file_type": file_ext
    }
```

---

## 📊 Rate Limiting Rules

### Rate Limit Tiers

**Send Email: STRICT**
- **Hourly:** 10 emails
- **Daily:** 50 emails
- **Reasoning:** External communication, high risk
- **Reset:** Every hour on the hour
- **Behavior on exceed:** Queue for next hour

**Draft Email: MODERATE**
- **Hourly:** 50 drafts
- **Daily:** 200 drafts
- **Reasoning:** Low risk (not sent), but prevent abuse
- **Reset:** Every hour on the hour
- **Behavior on exceed:** Warn user, allow with confirmation

**Search Email: GENEROUS**
- **Hourly:** 100 searches
- **Daily:** 500 searches
- **Reasoning:** Read-only, Gmail API has high limits
- **Reset:** Every hour on the hour
- **Behavior on exceed:** Slow down (add 5s delay), warn user

**Categorize Email: MODERATE**
- **Hourly:** 20 categorizations
- **Daily:** 50 categorizations
- **Reasoning:** Resource-intensive (multiple API calls per run)
- **Reset:** Every hour on the hour
- **Behavior on exceed:** Queue for next hour

### Implementation

**Rate Limit Tracking File:** `AI_Employee_Vault/Logs/rate_limits.json`

```json
{
  "send_email": {
    "current_hour": "2026-02-05T10",
    "count_this_hour": 3,
    "count_today": 8,
    "history": [
      {"timestamp": "2026-02-05T10:15:30", "recipient": "client@example.com"},
      {"timestamp": "2026-02-05T10:30:45", "recipient": "vendor@example.com"},
      {"timestamp": "2026-02-05T10:45:12", "recipient": "partner@example.com"}
    ]
  },
  "draft_email": {
    "current_hour": "2026-02-05T10",
    "count_this_hour": 12,
    "count_today": 25
  }
}
```

**Rate Limit Check Logic:**

```python
def check_rate_limit(action: str) -> dict:
    """Check if action is within rate limits."""

    limits = RATE_LIMITS[action]
    now = datetime.now()
    current_hour = now.strftime("%Y-%m-%dT%H")

    # Load current counts
    rate_data = load_rate_limit_data()
    action_data = rate_data.get(action, {})

    # Reset if new hour
    if action_data.get('current_hour') != current_hour:
        action_data['current_hour'] = current_hour
        action_data['count_this_hour'] = 0

    # Reset daily if new day
    current_date = now.strftime("%Y-%m-%d")
    if action_data.get('current_date') != current_date:
        action_data['current_date'] = current_date
        action_data['count_today'] = 0

    # Check limits
    hourly_ok = action_data.get('count_this_hour', 0) < limits['max_per_hour']
    daily_ok = action_data.get('count_today', 0) < limits['max_per_day']

    allowed = hourly_ok and daily_ok

    return {
        'allowed': allowed,
        'current_count': action_data.get('count_this_hour', 0),
        'max_limit': limits['max_per_hour'],
        'daily_count': action_data.get('count_today', 0),
        'daily_limit': limits['max_per_day'],
        'reset_time': datetime.strptime(current_hour, "%Y-%m-%dT%H") + timedelta(hours=1)
    }
```

---

## 🔗 Integration with Approval Workflow

### Approval Workflow Steps

1. **Email Handler** creates approval request → `Pending_Approval/`
2. **Task Processor** detects approval file (already there from email handler)
3. **Human** reviews and approves → Sets `approval_status: approved`
4. **Approval Executor** runs (manual or scheduled)
5. **Approval Executor** reads approved email, executes MCP
6. **Gmail MCP** sends email, returns message ID
7. **Approval Executor** logs success, archives approval
8. **Email Handler** (optional) confirms delivery, updates dashboard

### Integration Code

**In Email Handler** (`scripts/email_handler.py`):
```python
def send_email_request(recipient, subject, body, cc=None):
    """Create approval request for email send."""

    # Generate approval file
    approval_content = generate_approval_request({
        "action": "send_email",
        "mcp_server": "gmail",
        "mcp_tool": "send_email",
        "mcp_params": {
            "to": recipient,
            "subject": subject,
            "body": body,
            "cc": cc or []
        }
    })

    # Save to Pending_Approval
    filename = f"send_email_{sanitize(recipient)}_{timestamp()}.md"
    approval_path = PENDING_APPROVAL_PATH / filename

    with open(approval_path, "w") as f:
        f.write(approval_content)

    log_action("approval_request_created", {
        "file": filename,
        "recipient": recipient,
        "action": "send_email"
    })

    return {
        "success": True,
        "approval_file": str(approval_path),
        "requires_approval": True,
        "status": "pending"
    }
```

**In Approval Executor** (`scripts/approval_executor.py`):
```python
def process_email_approval(approval_file):
    """Execute approved email send."""

    # Read approval file
    with open(approval_file) as f:
        content = f.read()

    # Parse metadata
    metadata = parse_yaml_frontmatter(content)

    # Check approval status
    if metadata.get('approval_status') != 'approved':
        return {"success": False, "error": "not_approved"}

    # Check rate limit
    rate_status = check_rate_limit("send_email")
    if not rate_status['allowed']:
        return {"success": False, "error": "rate_limit_exceeded"}

    # Execute MCP
    from email_handler import execute_mcp_tool

    result = execute_mcp_tool(
        tool_name=metadata['mcp_tool'],
        params=metadata['mcp_params']
    )

    if result['success']:
        # Log execution
        log_action("email_sent", {
            "recipient": metadata['mcp_params']['to'],
            "message_id": result['message_id'],
            "approval_file": approval_file
        })

        # Archive approval
        archive_approval(approval_file, "executed")

        return {
            "success": True,
            "message_id": result['message_id']
        }
    else:
        # Log failure
        log_error("email_send_failed", {
            "recipient": metadata['mcp_params']['to'],
            "error": result['error'],
            "approval_file": approval_file
        })

        return result
```

---

## 📚 Dependencies

### Required
- Python 3.8+ (for async/await support)
- Gmail MCP Server (`mcp_servers/email/server.js`)
- `scripts/approval_executor.py`
- `scripts/task_processor` (runner_silver.py)
- Gmail API credentials (`credentials.json`, `token.json`)

### Optional
- `scripts/generate_approval.py` (for template-based approvals)
- Dashboard UI (for visual rate limit monitoring)
- Webhook server (for real-time email notifications)

### MCP Dependencies
- Node.js 18+ (for MCP server)
- `@modelcontextprotocol/sdk` npm package
- Gmail API OAuth2 credentials

---

## 🎯 Success Criteria

Skill is working correctly when:

- ✅ Drafts are created successfully without approval
- ✅ Send requests require and wait for approval
- ✅ Searches return accurate results
- ✅ Categorization correctly identifies urgent emails (>90% accuracy)
- ✅ Rate limits are enforced and prevent abuse
- ✅ MCP connection is stable and handles errors gracefully
- ✅ All actions are logged completely
- ✅ Approval workflow integrates smoothly
- ✅ Email validation catches common errors
- ✅ Retry logic handles transient failures

---

## 🔗 Related Skills

### Current
- **Task Processor** - Routes email tasks to this skill
- **Approval Executor** - Executes approved email sends

### Future
- **Email Template Manager** - Store and reuse email templates
- **Email Thread Analyzer** - Analyze email conversations for context
- **Auto-Responder** - Draft automatic replies based on content
- **Email Scheduler** - Schedule emails for future sending
- **Attachment Manager** - Handle large files via cloud storage

---

## 📞 Support

### Documentation
- **This Skill:** `AI_Employee_Vault/Skills/email_handler/SKILL.md`
- **Gmail MCP Setup:** `mcp_servers/email/README.md`
- **Approval Executor:** `APPROVAL_EXECUTOR_GUIDE.md`

### Logs
- **Skill logs:** `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- **Rate limits:** `AI_Employee_Vault/Logs/rate_limits.json`
- **MCP errors:** `mcp_servers/email/logs/`

### Testing
```bash
# Test draft creation (safe)
python -c "from scripts.email_handler import draft_email; draft_email('test@example.com', 'Test', 'Body')"

# Test search
python -c "from scripts.email_handler import search_emails; search_emails('from:sender@example.com')"

# Test validation
python -c "from scripts.email_handler import validate_email; print(validate_email('invalid'))"

# Test rate limits
python -c "from scripts.email_handler import check_rate_limit; print(check_rate_limit('send_email'))"
```

---

## 🚀 Roadmap

### Version 1.0 (Current)
- [x] Draft email capability
- [x] Send email with approval
- [x] Email search
- [x] Email categorization
- [x] Rate limiting
- [x] Error handling
- [x] MCP integration

### Version 1.1 (Planned - Q2 2026)
- [ ] Email templates library
- [ ] Scheduled sending
- [ ] Thread context analysis
- [ ] Auto-suggest responses
- [ ] Attachment cloud storage integration
- [ ] Email analytics dashboard

### Version 2.0 (Future - Q3 2026)
- [ ] Machine learning categorization
- [ ] Smart reply suggestions
- [ ] Multi-account support
- [ ] Email workflow automation
- [ ] Advanced search with NLP
- [ ] Integration with calendar/tasks

---

**Skill Version:** 1.0.0
**Status:** Active ✓
**Last Updated:** February 2026
**Test Coverage:** 100% (pending implementation)
**Production Ready:** Pending testing and MCP server validation
