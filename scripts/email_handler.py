#!/usr/bin/env python3
"""
Email Handler Skill - Implementation
Handles all email operations via Gmail MCP server with approval workflow integration.

Version: 1.0.0
Author: AI Employee System
"""

import os
import re
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_PATH = Path("./AI_Employee_Vault")
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DRAFTS_PATH = VAULT_PATH / "Drafts"
SEARCH_RESULTS_PATH = VAULT_PATH / "Search_Results"
REPORTS_PATH = VAULT_PATH / "Reports"
LOGS_PATH = VAULT_PATH / "Logs"

# Rate limits (per hour)
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

# Email categorization keywords
URGENT_KEYWORDS = [
    "urgent", "asap", "critical", "emergency", "immediate",
    "deadline", "today", "now", "escalate", "red alert"
]

QUESTION_INDICATORS = [
    "?", "can you", "could you", "please", "would you",
    "how", "what", "when", "where", "why", "who"
]

AUTOMATED_SENDERS = [
    "no-reply@", "noreply@", "donotreply@",
    "notifications@", "alerts@", "automated@"
]

NEWSLETTER_KEYWORDS = [
    "newsletter", "digest", "roundup", "weekly update",
    "monthly update", "unsubscribe", "view in browser"
]

# Allowed attachment types
ALLOWED_ATTACHMENT_TYPES = [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.zip'
]

MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024  # 25 MB


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_directories():
    """Ensure all required directories exist."""
    for path in [PENDING_APPROVAL_PATH, APPROVED_PATH, DRAFTS_PATH,
                 SEARCH_RESULTS_PATH, REPORTS_PATH, LOGS_PATH]:
        path.mkdir(parents=True, exist_ok=True)


def log_action(action_type: str, details: Dict) -> None:
    """Log action to daily JSON log file."""
    ensure_directories()

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "skill": "email_handler",
        "action": action_type,
        **details
    }

    # Read existing logs
    logs = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    # Append new log
    logs.append(log_entry)

    # Write back
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def log_error(error_type: str, details: Dict) -> None:
    """Log error with details."""
    log_action(f"error_{error_type}", {**details, "success": False})


def log_warning(warning_type: str, details: Dict) -> None:
    """Log warning with details."""
    log_action(f"warning_{warning_type}", details)


def update_dashboard_async(trigger_event: str) -> None:
    """Update dashboard asynchronously (non-blocking)."""
    try:
        from dashboard_updater import update_dashboard
        update_dashboard(trigger_event=trigger_event)
    except Exception:
        # Silently fail - dashboard update is not critical
        pass


def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filename."""
    # Remove invalid characters
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    # Limit length
    return text[:50]


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


# ============================================================================
# EMAIL VALIDATION
# ============================================================================

def validate_email(email: str) -> Dict:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        {
            'valid': bool,
            'error': str (if invalid),
            'suggestions': list (if invalid)
        }
    """
    # Basic format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        suggestions = []

        # Check for common typos
        if '@' not in email:
            # Find likely split point
            parts = email.split('.')
            if len(parts) > 1:
                suggestions.append(f"{parts[0]}@{'.'.join(parts[1:])}")

        # Common domain typos
        common_typos = {
            'gmial.com': 'gmail.com',
            'gmai.com': 'gmail.com',
            'gamil.com': 'gmail.com',
            'yahooo.com': 'yahoo.com',
            'yaho.com': 'yahoo.com',
            'hotmial.com': 'hotmail.com',
            'hotmali.com': 'hotmail.com'
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


def validate_attachment(file_path: str) -> Dict:
    """
    Validate attachment file.

    Args:
        file_path: Path to attachment file

    Returns:
        {
            'valid': bool,
            'error': str (if invalid),
            'suggestion': str (if invalid),
            'file_size': int (if valid),
            'file_type': str (if valid)
        }
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "valid": False,
            "error": "file_not_found",
            "message": f"File not found: {file_path}"
        }

    # Check file size
    file_size = os.path.getsize(file_path)

    if file_size > MAX_ATTACHMENT_SIZE:
        size_mb = file_size / (1024 * 1024)
        return {
            "valid": False,
            "error": "file_too_large",
            "message": f"File too large: {size_mb:.1f} MB (limit: 25 MB)",
            "suggestion": "Upload to Google Drive/Dropbox and share link instead"
        }

    # Check file type
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext not in ALLOWED_ATTACHMENT_TYPES:
        return {
            "valid": False,
            "error": "invalid_file_type",
            "message": f"File type not allowed: {file_ext}",
            "allowed_types": ALLOWED_ATTACHMENT_TYPES
        }

    return {
        "valid": True,
        "file_size": file_size,
        "file_type": file_ext
    }


# ============================================================================
# RATE LIMITING
# ============================================================================

def load_rate_limit_data() -> Dict:
    """Load rate limit tracking data."""
    rate_limit_file = LOGS_PATH / "rate_limits.json"

    if rate_limit_file.exists():
        try:
            with open(rate_limit_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    return {}


def save_rate_limit_data(data: Dict) -> None:
    """Save rate limit tracking data."""
    ensure_directories()
    rate_limit_file = LOGS_PATH / "rate_limits.json"

    with open(rate_limit_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check_rate_limit(action: str) -> Dict:
    """
    Check if action is within rate limits.

    Args:
        action: Action type ('send_email', 'draft_email', etc.)

    Returns:
        {
            'allowed': bool,
            'current_count': int,
            'max_limit': int,
            'daily_count': int,
            'daily_limit': int,
            'reset_time': str
        }
    """
    if action not in RATE_LIMITS:
        return {"allowed": True, "error": "Unknown action type"}

    limits = RATE_LIMITS[action]
    now = datetime.now()
    current_hour = now.strftime("%Y-%m-%dT%H")
    current_date = now.strftime("%Y-%m-%d")

    # Load current counts
    rate_data = load_rate_limit_data()
    action_data = rate_data.get(action, {})

    # Reset if new hour
    if action_data.get('current_hour') != current_hour:
        action_data['current_hour'] = current_hour
        action_data['count_this_hour'] = 0

    # Reset daily if new day
    if action_data.get('current_date') != current_date:
        action_data['current_date'] = current_date
        action_data['count_today'] = 0
        action_data['history'] = []

    # Check limits
    count_this_hour = action_data.get('count_this_hour', 0)
    count_today = action_data.get('count_today', 0)

    hourly_ok = count_this_hour < limits['max_per_hour']
    daily_ok = count_today < limits['max_per_day']

    allowed = hourly_ok and daily_ok

    # Calculate reset time
    reset_time = datetime.strptime(current_hour, "%Y-%m-%dT%H") + timedelta(hours=1)

    return {
        'allowed': allowed,
        'current_count': count_this_hour,
        'max_limit': limits['max_per_hour'],
        'daily_count': count_today,
        'daily_limit': limits['max_per_day'],
        'reset_time': reset_time.isoformat()
    }


def increment_rate_limit(action: str, details: Dict = None) -> None:
    """
    Increment rate limit counter for action.

    Args:
        action: Action type
        details: Optional details to store (recipient, subject, etc.)
    """
    rate_data = load_rate_limit_data()

    if action not in rate_data:
        rate_data[action] = {}

    action_data = rate_data[action]

    # Increment counts
    action_data['count_this_hour'] = action_data.get('count_this_hour', 0) + 1
    action_data['count_today'] = action_data.get('count_today', 0) + 1

    # Add to history
    if 'history' not in action_data:
        action_data['history'] = []

    history_entry = {
        "timestamp": datetime.now().isoformat(),
        **(details or {})
    }
    action_data['history'].append(history_entry)

    # Keep only last 100 entries
    action_data['history'] = action_data['history'][-100:]

    save_rate_limit_data(rate_data)


# ============================================================================
# MCP INTEGRATION (Placeholder - requires actual MCP client)
# ============================================================================

async def execute_mcp_tool(tool_name: str, params: Dict, retry: bool = True) -> Dict:
    """
    Execute Gmail MCP tool with error handling and retry logic.

    Args:
        tool_name: MCP tool name ('send_email', 'create_draft', 'search_emails')
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
    max_retries = 3 if retry else 1
    attempts = []

    for attempt in range(1, max_retries + 1):
        try:
            # TODO: Replace with actual MCP client call
            # This is a placeholder implementation

            # For now, simulate MCP call
            print(f"[MCP] Calling tool: {tool_name}")
            print(f"[MCP] Parameters: {json.dumps(params, indent=2)}")

            # Simulated response
            if tool_name == "create_draft":
                result = {
                    "success": True,
                    "draft_id": f"draft_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "created_at": datetime.now().isoformat()
                }
            elif tool_name == "send_email":
                result = {
                    "success": True,
                    "message_id": f"msg_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "sent_at": datetime.now().isoformat()
                }
            elif tool_name == "search_emails":
                result = {
                    "success": True,
                    "count": 0,
                    "results": []
                }
            else:
                result = {"success": True}

            return {
                "success": True,
                "result": result,
                "attempts": attempt
            }

        except Exception as e:
            attempts.append({
                "attempt": attempt,
                "error": str(e),
                "error_type": "exception"
            })

            log_error("mcp_tool_execution_failed", {
                "tool_name": tool_name,
                "attempt": attempt,
                "error": str(e)
            })

            # Retry with exponential backoff
            if attempt < max_retries:
                wait_time = 2 ** attempt  # 2s, 4s, 8s
                await asyncio.sleep(wait_time)

    # All retries failed
    return {
        "success": False,
        "error": "execution_failed_after_retries",
        "attempts": attempts
    }


# ============================================================================
# DRAFT EMAIL
# ============================================================================

def draft_email(recipient: str, subject: str, body: str, cc: List[str] = None) -> Dict:
    """
    Create email draft via Gmail MCP (no approval needed).

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
    ensure_directories()

    # Validate recipient
    validation = validate_email(recipient)
    if not validation['valid']:
        log_error("draft_email_invalid_recipient", {
            "recipient": recipient,
            "error": validation['error']
        })
        return {
            "success": False,
            "error": validation['error'],
            "suggestions": validation.get('suggestions', [])
        }

    # Check rate limit
    rate_status = check_rate_limit('draft_email')
    if not rate_status['allowed']:
        log_warning("draft_email_rate_limit", {
            "recipient": recipient,
            "current_count": rate_status['current_count'],
            "max_limit": rate_status['max_limit']
        })
        return {
            "success": False,
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {rate_status['current_count']}/{rate_status['max_limit']} drafts this hour",
            "reset_time": rate_status['reset_time']
        }

    # Execute MCP call (synchronous wrapper for async)
    try:
        result = asyncio.run(execute_mcp_tool("create_draft", {
            "to": recipient,
            "subject": subject,
            "body": body,
            "cc": cc or []
        }))

        if not result['success']:
            log_error("draft_email_mcp_failed", {
                "recipient": recipient,
                "error": result.get('error')
            })
            return result

        # Get draft ID from result
        draft_id = result['result']['draft_id']

        # Save draft record locally
        draft_filename = f"{sanitize_filename(subject)}_draft.md"
        draft_path = DRAFTS_PATH / draft_filename

        draft_content = f"""---
action: draft_email
status: completed
created_at: {get_timestamp()}
recipient: {recipient}
subject: {subject}
draft_id: {draft_id}
mcp_server: gmail
mcp_tool: create_draft
---

# Email Draft: {subject}

**To:** {recipient}
{f"**Cc:** {', '.join(cc)}" if cc else ""}
**Subject:** {subject}
**Draft ID:** {draft_id}

## Email Content

{body}

---

## Actions Available
- [ ] Edit draft (manual in Gmail)
- [ ] Request approval to send
- [ ] Discard draft
"""

        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(draft_content)

        # Increment rate limit
        increment_rate_limit('draft_email', {
            "recipient": recipient,
            "subject": subject,
            "draft_id": draft_id
        })

        # Log success
        log_action("draft_email_success", {
            "recipient": recipient,
            "subject": subject,
            "draft_id": draft_id,
            "saved_to": str(draft_path),
            "success": True
        })

        # Update dashboard
        update_dashboard_async("email_draft_created")

        return {
            "success": True,
            "draft_id": draft_id,
            "saved_to": str(draft_path),
            "message": f"Draft created successfully! Draft ID: {draft_id}"
        }

    except Exception as e:
        log_error("draft_email_exception", {
            "recipient": recipient,
            "error": str(e)
        })
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# SEND EMAIL (REQUIRES APPROVAL)
# ============================================================================

def send_email_request(recipient: str, subject: str, body: str,
                       cc: List[str] = None, bcc: List[str] = None,
                       attachments: List[str] = None) -> Dict:
    """
    Create approval request for sending email.

    Args:
        recipient: Email address
        subject: Email subject
        body: Email content
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        attachments: Optional attachment file paths

    Returns:
        {
            'success': bool,
            'approval_file': str,
            'requires_approval': bool,
            'status': str
        }
    """
    ensure_directories()

    # Validate recipient
    validation = validate_email(recipient)
    if not validation['valid']:
        log_error("send_email_invalid_recipient", {
            "recipient": recipient,
            "error": validation['error']
        })
        return {
            "success": False,
            "error": validation['error'],
            "suggestions": validation.get('suggestions', [])
        }

    # Validate attachments if provided
    if attachments:
        for attachment in attachments:
            validation = validate_attachment(attachment)
            if not validation['valid']:
                log_error("send_email_invalid_attachment", {
                    "recipient": recipient,
                    "attachment": attachment,
                    "error": validation['error']
                })
                return {
                    "success": False,
                    "error": validation['error'],
                    "suggestion": validation.get('suggestion')
                }

    # Check rate limit
    rate_status = check_rate_limit('send_email')
    if not rate_status['allowed']:
        log_warning("send_email_rate_limit", {
            "recipient": recipient,
            "current_count": rate_status['current_count'],
            "max_limit": rate_status['max_limit']
        })
        return {
            "success": False,
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {rate_status['current_count']}/{rate_status['max_limit']} emails this hour",
            "reset_time": rate_status['reset_time']
        }

    # Generate approval request
    timestamp = get_timestamp()
    expires_at = (datetime.now() + timedelta(days=1)).isoformat()

    approval_filename = f"send_{sanitize_filename(recipient)}_{sanitize_filename(subject)}.md"
    approval_path = PENDING_APPROVAL_PATH / approval_filename

    # Build MCP params
    mcp_params = {
        "to": recipient,
        "subject": subject,
        "body": body,
        "cc": cc or [],
        "bcc": bcc or [],
        "attachments": attachments or []
    }

    approval_content = f"""---
action: send_email
mcp_server: gmail
mcp_tool: send_email
mcp_params:
  to: {recipient}
  subject: {subject}
  body: |
{chr(10).join('    ' + line for line in body.split(chr(10)))}
  cc: {json.dumps(cc or [])}
  bcc: {json.dumps(bcc or [])}
  attachments: {json.dumps(attachments or [])}
requires_approval: true
approval_status: pending
created_at: {timestamp}
expires_at: {expires_at}
retry_config:
  max_retries: 3
  retry_delay: 60
  exponential_backoff: true
rate_limit:
  max_per_hour: 10
  current_count: {rate_status['current_count']}
security_checklist:
  - recipient_verified: false
  - content_reviewed: false
  - attachments_scanned: false
  - compliance_checked: false
---

# Approval Request: Send Email

## Action Summary
**Type:** Send Email via Gmail MCP
**Recipient:** {recipient}
**Subject:** {subject}
**Priority:** {"High" if "urgent" in subject.lower() or "urgent" in body.lower() else "Medium"}
**Created:** {timestamp}
**Expires:** {expires_at}

## Email Preview

**To:** {recipient}
{f"**Cc:** {', '.join(cc)}" if cc else ""}
{f"**Bcc:** {', '.join(bcc)}" if bcc else ""}
**Subject:** {subject}

```
{body}
```

{f"**Attachments:** {len(attachments)} file(s)" if attachments else "**Attachments:** None"}

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
**Rate Limit:** {rate_status['current_count']}/{rate_status['max_limit']} emails this hour
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
- {"Client-facing" if "client" in recipient.lower() else "Business communication"}

**Mitigation:**
- Human approval required
- Content review
- Rate limiting enforced
- Audit log maintained
"""

    # Save approval request
    with open(approval_path, "w", encoding="utf-8") as f:
        f.write(approval_content)

    # Log approval request creation
    log_action("send_email_approval_created", {
        "recipient": recipient,
        "subject": subject,
        "approval_file": str(approval_path),
        "approval_status": "pending",
        "success": True
    })

    # Update dashboard
    update_dashboard_async("email_approval_created")

    return {
        "success": True,
        "approval_file": str(approval_path),
        "requires_approval": True,
        "status": "pending",
        "message": f"Email send request created. Approval required in: {approval_path}"
    }


# ============================================================================
# SEARCH EMAILS
# ============================================================================

def search_emails(query: str, max_results: int = 50) -> Dict:
    """
    Search Gmail inbox with query.

    Args:
        query: Gmail search query string
        max_results: Maximum results to return

    Returns:
        {
            'success': bool,
            'count': int,
            'results': list,
            'saved_to': str
        }
    """
    ensure_directories()

    # Check rate limit
    rate_status = check_rate_limit('search_emails')
    if not rate_status['allowed']:
        log_warning("search_emails_rate_limit", {
            "query": query,
            "current_count": rate_status['current_count']
        })
        return {
            "success": False,
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {rate_status['current_count']}/{rate_status['max_limit']} searches this hour"
        }

    # Execute MCP search
    try:
        result = asyncio.run(execute_mcp_tool("search_emails", {
            "query": query,
            "max_results": max_results
        }))

        if not result['success']:
            log_error("search_emails_mcp_failed", {
                "query": query,
                "error": result.get('error')
            })
            return result

        # Get results
        search_result = result['result']
        count = search_result.get('count', 0)
        results = search_result.get('results', [])

        # Save results to file
        results_filename = f"{sanitize_filename(query)}_results.md"
        results_path = SEARCH_RESULTS_PATH / results_filename

        results_content = f"""---
action: search_emails
status: completed
query: {query}
results_count: {count}
search_date: {get_timestamp()}
mcp_server: gmail
mcp_tool: search_emails
---

# Email Search Results

**Query:** {query}
**Results:** {count} emails found
**Search Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Results

"""

        if count == 0:
            results_content += "No emails found matching the search criteria.\n"
        else:
            for i, email in enumerate(results, 1):
                results_content += f"""### {i}. {email.get('subject', 'No Subject')}
- **From:** {email.get('from', 'Unknown')}
- **Date:** {email.get('date', 'Unknown')}
- **Preview:** {email.get('preview', 'No preview available')[:100]}...
- **Message ID:** {email.get('id', 'Unknown')}
- **Labels:** {', '.join(email.get('labels', []))}

"""

        results_content += """
## Actions Available
- [ ] Read full email content
- [ ] Download attachments
- [ ] Reply to email (requires approval)
- [ ] Archive emails
- [ ] Apply labels
"""

        with open(results_path, "w", encoding="utf-8") as f:
            f.write(results_content)

        # Increment rate limit
        increment_rate_limit('search_emails', {
            "query": query,
            "results_count": count
        })

        # Log success
        log_action("search_emails_success", {
            "query": query,
            "results_count": count,
            "saved_to": str(results_path),
            "success": True
        })

        # Update dashboard
        update_dashboard_async("email_search_performed")

        return {
            "success": True,
            "count": count,
            "results": results,
            "saved_to": str(results_path),
            "message": f"Found {count} emails. Results saved to: {results_path}"
        }

    except Exception as e:
        log_error("search_emails_exception", {
            "query": query,
            "error": str(e)
        })
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# CATEGORIZE EMAILS
# ============================================================================

def categorize_emails(date_range: str = "last_7_days") -> Dict:
    """
    Categorize emails by urgency and type.

    Args:
        date_range: Time range to analyze ('last_7_days', 'last_3_days', etc.)

    Returns:
        {
            'success': bool,
            'total_emails': int,
            'categories': dict,
            'recommendations': list,
            'report_file': str
        }
    """
    ensure_directories()

    # Check rate limit
    rate_status = check_rate_limit('categorize_emails')
    if not rate_status['allowed']:
        log_warning("categorize_emails_rate_limit", {
            "current_count": rate_status['current_count']
        })
        return {
            "success": False,
            "error": "rate_limit_exceeded",
            "message": f"Rate limit exceeded: {rate_status['current_count']}/{rate_status['max_limit']} categorizations this hour"
        }

    # Parse date range
    if date_range == "last_7_days":
        days = 7
    elif date_range == "last_3_days":
        days = 3
    elif date_range == "last_30_days":
        days = 30
    else:
        days = 7  # default

    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

    # Build query
    query = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"

    # Search for emails
    search_result = search_emails(query, max_results=100)

    if not search_result['success']:
        return search_result

    emails = search_result['results']
    total_emails = len(emails)

    # Categorize each email
    categories = {
        "urgent": [],
        "needs_response": [],
        "fyi": [],
        "archive": []
    }

    for email in emails:
        category = _categorize_single_email(email)
        categories[category].append(email)

    # Generate recommendations
    recommendations = _generate_recommendations(categories)

    # Create report
    report_filename = f"email_categorization_{datetime.now().strftime('%Y-%m-%d')}.md"
    report_path = REPORTS_PATH / report_filename

    report_content = f"""---
action: categorize_emails
status: completed
date_range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
total_emails: {total_emails}
categorized_at: {get_timestamp()}
---

# Email Categorization Report

**Period:** {start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}
**Total Emails:** {total_emails}
**Processed:** {total_emails} (100%)

## Category Breakdown

### 🔴 Urgent Action Required ({len(categories['urgent'])} emails)
"""

    for i, email in enumerate(categories['urgent'][:10], 1):
        report_content += f"{i}. **{email.get('subject', 'No Subject')}** - {email.get('from', 'Unknown')} - {email.get('date', 'Unknown')}\n"

    report_content += f"""
### 🟡 Needs Response ({len(categories['needs_response'])} emails)
"""

    for i, email in enumerate(categories['needs_response'][:10], 1):
        report_content += f"{i}. **{email.get('subject', 'No Subject')}** - {email.get('from', 'Unknown')} - {email.get('date', 'Unknown')}\n"

    report_content += f"""
### 🔵 FYI / Informational ({len(categories['fyi'])} emails)
"""

    for i, email in enumerate(categories['fyi'][:5], 1):
        report_content += f"{i}. **{email.get('subject', 'No Subject')}** - {email.get('from', 'Unknown')} - {email.get('date', 'Unknown')}\n"

    report_content += f"""
### ⚪ Archive ({len(categories['archive'])} emails)
"""

    for i, email in enumerate(categories['archive'][:5], 1):
        report_content += f"{i}. **{email.get('subject', 'No Subject')}** - {email.get('from', 'Unknown')} - {email.get('date', 'Unknown')}\n"

    report_content += """
## Recommended Actions

"""

    for i, rec in enumerate(recommendations, 1):
        report_content += f"{i}. {rec}\n"

    report_content += f"""
## Statistics

- Emails requiring action: {len(categories['urgent']) + len(categories['needs_response'])} ({((len(categories['urgent']) + len(categories['needs_response'])) / total_emails * 100):.0f}%)
- Urgent emails: {len(categories['urgent'])} ({(len(categories['urgent']) / total_emails * 100):.0f}%)
- Informational: {len(categories['fyi'])} ({(len(categories['fyi']) / total_emails * 100):.0f}%)
- Can be archived: {len(categories['archive'])} ({(len(categories['archive']) / total_emails * 100):.0f}%)
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    # Increment rate limit
    increment_rate_limit('categorize_emails', {
        "date_range": date_range,
        "total_emails": total_emails
    })

    # Log success
    log_action("categorize_emails_success", {
        "date_range": date_range,
        "total_emails": total_emails,
        "urgent": len(categories['urgent']),
        "needs_response": len(categories['needs_response']),
        "fyi": len(categories['fyi']),
        "archive": len(categories['archive']),
        "report_file": str(report_path),
        "success": True
    })

    # Update dashboard
    update_dashboard_async("email_categorization_complete")

    return {
        "success": True,
        "total_emails": total_emails,
        "categories": {
            "urgent": len(categories['urgent']),
            "needs_response": len(categories['needs_response']),
            "fyi": len(categories['fyi']),
            "archive": len(categories['archive'])
        },
        "recommendations": recommendations,
        "report_file": str(report_path),
        "message": f"Categorized {total_emails} emails. Report: {report_path}"
    }


def _categorize_single_email(email: Dict) -> str:
    """Categorize a single email based on content."""
    subject = email.get('subject', '').lower()
    sender = email.get('from', '').lower()
    preview = email.get('preview', '').lower()
    labels = [label.lower() for label in email.get('labels', [])]

    content = f"{subject} {preview}"

    # Check for urgent keywords
    if any(keyword in content for keyword in URGENT_KEYWORDS):
        return "urgent"

    # Check if it's from automated sender
    if any(auto in sender for auto in AUTOMATED_SENDERS):
        return "archive"

    # Check if it's a newsletter
    if any(keyword in content for keyword in NEWSLETTER_KEYWORDS):
        return "fyi"

    # Check if it contains questions (needs response)
    if any(indicator in content for indicator in QUESTION_INDICATORS):
        return "needs_response"

    # Check if it has important label
    if 'important' in labels or 'starred' in labels:
        return "needs_response"

    # Check if unread (might need response)
    if 'unread' in labels:
        return "needs_response"

    # Default to FYI
    return "fyi"


def _generate_recommendations(categories: Dict) -> List[str]:
    """Generate action recommendations based on categorization."""
    recommendations = []

    if categories['urgent']:
        urgent_email = categories['urgent'][0]
        recommendations.append(
            f"**URGENT:** Address '{urgent_email.get('subject', 'urgent issue')}' from {urgent_email.get('from', 'sender')} immediately"
        )

    if len(categories['needs_response']) > 5:
        recommendations.append(
            f"**High Priority:** {len(categories['needs_response'])} emails need responses. Schedule time to reply today."
        )
    elif categories['needs_response']:
        recommendations.append(
            f"**Medium Priority:** Reply to {len(categories['needs_response'])} emails within 24 hours"
        )

    if len(categories['fyi']) > 20:
        recommendations.append(
            f"**Low Priority:** {len(categories['fyi'])} informational emails. Review when time permits."
        )

    if categories['archive']:
        recommendations.append(
            f"**Maintenance:** {len(categories['archive'])} emails can be archived to clean up inbox"
        )

    return recommendations


# ============================================================================
# MAIN / CLI
# ============================================================================

if __name__ == "__main__":
    import sys

    ensure_directories()

    if len(sys.argv) < 2:
        print("Email Handler Skill - Usage:")
        print()
        print("  Draft email:")
        print("    python email_handler.py draft <recipient> <subject> <body>")
        print()
        print("  Send email (creates approval):")
        print("    python email_handler.py send <recipient> <subject> <body>")
        print()
        print("  Search emails:")
        print("    python email_handler.py search <query>")
        print()
        print("  Categorize emails:")
        print("    python email_handler.py categorize [date_range]")
        print()
        print("  Check rate limit:")
        print("    python email_handler.py ratelimit <action>")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "draft":
        if len(sys.argv) < 5:
            print("Error: Missing arguments for draft")
            print("Usage: python email_handler.py draft <recipient> <subject> <body>")
            sys.exit(1)

        result = draft_email(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))

    elif command == "send":
        if len(sys.argv) < 5:
            print("Error: Missing arguments for send")
            print("Usage: python email_handler.py send <recipient> <subject> <body>")
            sys.exit(1)

        result = send_email_request(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(result, indent=2))

    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Missing query for search")
            print("Usage: python email_handler.py search <query>")
            sys.exit(1)

        result = search_emails(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif command == "categorize":
        date_range = sys.argv[2] if len(sys.argv) > 2 else "last_7_days"
        result = categorize_emails(date_range)
        print(json.dumps(result, indent=2))

    elif command == "ratelimit":
        if len(sys.argv) < 3:
            print("Error: Missing action for rate limit check")
            print("Usage: python email_handler.py ratelimit <action>")
            sys.exit(1)

        result = check_rate_limit(sys.argv[2])
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
