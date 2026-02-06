#!/usr/bin/env python3
"""
Gmail Inbox Watcher for AI Employee System

Monitors Gmail inbox for important emails and automatically creates task files
in Needs_Action/ for processing by the task processor.

Features:
- Polls every 2 minutes for new unread important emails
- Filters by importance, sender, and keywords
- Creates task files with email metadata
- Marks emails as read after processing
- Rate limiting (max 50 emails/hour)
- OAuth token refresh handling
- Error recovery for API failures
- Test mode and dry-run mode

Usage:
    python watchers/gmail_watcher.py                  # Normal mode
    python watchers/gmail_watcher.py --test           # Test mode (no marking as read)
    python watchers/gmail_watcher.py --dry-run        # Dry run (no task creation)
    python watchers/gmail_watcher.py --once           # Process once and exit

Requirements:
    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

Version: 1.0.0
Author: AI Employee System
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try to import Google libraries
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print("[ERROR] Required Google libraries not found.")
    print("\nPlease install them with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "AI_Employee_Vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"

# Gmail API credentials paths
MCP_EMAIL_DIR = PROJECT_ROOT / "mcp_servers" / "email"
CREDENTIALS_FILE = MCP_EMAIL_DIR / "config.json"
TOKEN_FILE = MCP_EMAIL_DIR / "token.json"

# Gmail API scopes (must match the OAuth setup)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
]

# Polling configuration
POLL_INTERVAL = 120  # seconds (2 minutes)
MAX_RESULTS = 50     # max emails to fetch per poll

# Rate limiting
MAX_EMAILS_PER_HOUR = 50
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Email filtering configuration
IMPORTANT_KEYWORDS = [
    'urgent', 'asap', 'critical', 'emergency', 'immediate',
    'invoice', 'payment', 'help', 'problem', 'issue', 'deadline'
]

# Client email patterns (customize these)
CLIENT_DOMAINS = [
    '@client.com', '@customer.com', '@partner.com'
]

# Priority mapping
PRIORITY_KEYWORDS = {
    'high': ['urgent', 'asap', 'critical', 'emergency', 'immediate', 'deadline'],
    'medium': ['invoice', 'payment', 'help', 'problem', 'issue'],
    'low': []
}


# ============================================================================
# GMAIL API CLIENT
# ============================================================================

class GmailWatcher:
    """Watches Gmail inbox and creates tasks for important emails."""

    def __init__(self, test_mode: bool = False, dry_run: bool = False):
        """
        Initialize Gmail watcher.

        Args:
            test_mode: If True, don't mark emails as read
            dry_run: If True, don't create task files
        """
        self.test_mode = test_mode
        self.dry_run = dry_run
        self.service = None
        self.processed_count = 0
        self.rate_limit_tracker = []

        # Ensure directories exist
        NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
        LOGS_PATH.mkdir(parents=True, exist_ok=True)

        self.log(f"Gmail Watcher initialized (test_mode={test_mode}, dry_run={dry_run})")

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }.get(level, "•")

        # Use simple ASCII for Windows compatibility
        prefix_ascii = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "WARNING": "[WARN]",
            "ERROR": "[ERROR]"
        }.get(level, "")

        print(f"{timestamp} {prefix_ascii} {message}")

    def log_to_json(self, action: str, details: Dict):
        """Log action to daily JSON log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS_PATH / f"{today}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": "gmail_watcher",
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

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.

        Returns:
            True if authentication successful, False otherwise
        """
        creds = None

        # Check if we have a token file
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
                self.log("Loaded existing credentials from token.json")
            except Exception as e:
                self.log(f"Failed to load token.json: {e}", "WARNING")
                creds = None

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    self.log("Refreshing expired credentials...")
                    creds.refresh(Request())
                    self.log("Credentials refreshed successfully", "SUCCESS")
                except Exception as e:
                    self.log(f"Failed to refresh credentials: {e}", "ERROR")
                    self.log("Please run: python scripts/setup_gmail_oauth.py", "WARNING")
                    return False
            else:
                # No valid credentials, need to authenticate
                if not CREDENTIALS_FILE.exists():
                    self.log(f"Credentials file not found: {CREDENTIALS_FILE}", "ERROR")
                    self.log("Please run: python scripts/setup_gmail_oauth.py", "WARNING")
                    return False

                try:
                    self.log("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_FILE), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    self.log("OAuth flow completed successfully", "SUCCESS")
                except Exception as e:
                    self.log(f"OAuth flow failed: {e}", "ERROR")
                    return False

            # Save the credentials for the next run
            try:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                self.log("Credentials saved to token.json", "SUCCESS")
            except Exception as e:
                self.log(f"Failed to save credentials: {e}", "WARNING")

        # Build the Gmail API service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.log("Gmail API service initialized", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to build Gmail service: {e}", "ERROR")
            return False

    def check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns:
            True if within limits, False if exceeded
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)

        # Remove old entries
        self.rate_limit_tracker = [
            ts for ts in self.rate_limit_tracker
            if ts > cutoff
        ]

        # Check if under limit
        if len(self.rate_limit_tracker) >= MAX_EMAILS_PER_HOUR:
            self.log(f"Rate limit exceeded: {len(self.rate_limit_tracker)}/{MAX_EMAILS_PER_HOUR} per hour", "WARNING")
            return False

        return True

    def record_processed_email(self):
        """Record that an email was processed for rate limiting."""
        self.rate_limit_tracker.append(datetime.now())
        self.processed_count += 1

    def build_search_query(self) -> str:
        """
        Build Gmail search query for important emails.

        Returns:
            Gmail search query string
        """
        query_parts = [
            "is:unread",
            "in:inbox",
        ]

        # Add importance filter OR client filter
        importance_parts = [
            "is:important",
            f"from:({' OR '.join(CLIENT_DOMAINS)})"
        ]

        # Add keyword filters
        keyword_filter = ' OR '.join([f'subject:{kw}' for kw in IMPORTANT_KEYWORDS])

        # Combine: unread AND inbox AND (important OR from:clients OR keywords)
        query = f"{' '.join(query_parts)} ({' OR '.join(importance_parts)} OR ({keyword_filter}))"

        return query

    def fetch_important_emails(self) -> List[Dict]:
        """
        Fetch important unread emails from Gmail.

        Returns:
            List of email message dictionaries
        """
        if not self.service:
            self.log("Gmail service not initialized", "ERROR")
            return []

        try:
            # Build search query
            query = self.build_search_query()
            self.log(f"Searching with query: {query[:100]}...")

            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=MAX_RESULTS
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                self.log("No new important emails found")
                return []

            self.log(f"Found {len(messages)} important email(s)", "SUCCESS")

            # Fetch full message details
            emails = []
            for msg in messages:
                try:
                    # Check rate limit before processing each email
                    if not self.check_rate_limit():
                        self.log("Rate limit reached, stopping email fetch", "WARNING")
                        break

                    email_data = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    emails.append(email_data)

                except HttpError as e:
                    self.log(f"Failed to fetch email {msg['id']}: {e}", "ERROR")
                    continue

            return emails

        except HttpError as e:
            self.log(f"Gmail API error: {e}", "ERROR")
            self.log_to_json("gmail_api_error", {"error": str(e)})
            return []

    def extract_email_info(self, email_data: Dict) -> Dict:
        """
        Extract relevant information from email data.

        Args:
            email_data: Gmail API message object

        Returns:
            Dictionary with extracted email information
        """
        headers = {h['name']: h['value'] for h in email_data['payload']['headers']}

        # Extract basic info
        info = {
            'message_id': email_data['id'],
            'thread_id': email_data['threadId'],
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', 'Unknown'),
            'subject': headers.get('Subject', '(No Subject)'),
            'date': headers.get('Date', ''),
            'labels': email_data.get('labelIds', []),
            'snippet': email_data.get('snippet', '')[:200],  # First 200 chars
        }

        # Extract sender email
        from_header = info['from']
        email_match = re.search(r'<(.+?)>', from_header)
        if email_match:
            info['sender_email'] = email_match.group(1)
        else:
            info['sender_email'] = from_header

        # Determine priority based on keywords
        subject_lower = info['subject'].lower()
        snippet_lower = info['snippet'].lower()

        priority = 'low'
        for level in ['high', 'medium']:
            for keyword in PRIORITY_KEYWORDS[level]:
                if keyword in subject_lower or keyword in snippet_lower:
                    priority = level
                    break
            if priority == level:
                break

        info['priority'] = priority

        # Check if from client domain
        info['is_client'] = any(domain in info['sender_email'] for domain in CLIENT_DOMAINS)

        # Check if important label
        info['is_important'] = 'IMPORTANT' in info['labels']

        return info

    def create_task_file(self, email_info: Dict) -> Optional[Path]:
        """
        Create a task file in Needs_Action/ for the email.

        Args:
            email_info: Extracted email information

        Returns:
            Path to created task file, or None if creation failed
        """
        if self.dry_run:
            self.log(f"[DRY-RUN] Would create task for: {email_info['subject']}")
            return None

        try:
            # Generate filename (sanitize subject)
            subject_clean = re.sub(r'[^\w\s-]', '', email_info['subject'])
            subject_clean = re.sub(r'[-\s]+', '_', subject_clean)
            subject_clean = subject_clean[:50]  # Max 50 chars

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_{timestamp}_{subject_clean}.md"
            filepath = NEEDS_ACTION_PATH / filename

            # Build task content
            content = f"""---
createdAt: {datetime.now().isoformat()}
source: gmail_watcher
status: needs_action
type: email_task
priority: {email_info['priority']}
email_metadata:
  message_id: {email_info['message_id']}
  thread_id: {email_info['thread_id']}
  from: {email_info['sender_email']}
  subject: "{email_info['subject']}"
  date: {email_info['date']}
  is_important: {email_info['is_important']}
  is_client: {email_info['is_client']}
  labels: {json.dumps(email_info['labels'])}
---

# Email: {email_info['subject']}

**From:** {email_info['from']}
**Date:** {email_info['date']}
**Priority:** {email_info['priority'].upper()}

## Email Preview

{email_info['snippet']}

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

**Message ID:** {email_info['message_id']}
**Thread ID:** {email_info['thread_id']}
"""

            # Write task file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log(f"Created task file: {filename}", "SUCCESS")
            return filepath

        except Exception as e:
            self.log(f"Failed to create task file: {e}", "ERROR")
            return None

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark email as read in Gmail.

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        if self.test_mode:
            self.log(f"[TEST MODE] Would mark message {message_id} as read")
            return True

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            self.log(f"Marked message {message_id} as read", "SUCCESS")
            return True

        except HttpError as e:
            self.log(f"Failed to mark message {message_id} as read: {e}", "ERROR")
            return False

    def process_email(self, email_data: Dict) -> bool:
        """
        Process a single email: extract info, create task, mark as read.

        Args:
            email_data: Gmail API message object

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Extract email information
            email_info = self.extract_email_info(email_data)

            self.log(f"Processing: {email_info['subject'][:50]}...")

            # Create task file
            task_file = self.create_task_file(email_info)

            if task_file or self.dry_run:
                # Mark as read
                if self.mark_as_read(email_info['message_id']):
                    # Log to JSON
                    self.log_to_json("email_processed", {
                        "message_id": email_info['message_id'],
                        "from": email_info['sender_email'],
                        "subject": email_info['subject'],
                        "priority": email_info['priority'],
                        "task_file": str(task_file) if task_file else None,
                        "test_mode": self.test_mode,
                        "dry_run": self.dry_run
                    })

                    # Record for rate limiting
                    self.record_processed_email()

                    return True

            return False

        except Exception as e:
            self.log(f"Error processing email: {e}", "ERROR")
            return False

    def run_once(self) -> int:
        """
        Run one cycle of email checking and processing.

        Returns:
            Number of emails processed
        """
        self.log("Starting email check cycle...")

        # Fetch important emails
        emails = self.fetch_important_emails()

        if not emails:
            return 0

        # Process each email
        processed = 0
        for email_data in emails:
            if self.process_email(email_data):
                processed += 1
            else:
                self.log("Failed to process email, skipping...", "WARNING")

        self.log(f"Cycle complete: {processed}/{len(emails)} emails processed", "SUCCESS")

        return processed

    def run_continuous(self):
        """Run continuous monitoring loop."""
        self.log(f"Starting continuous monitoring (poll interval: {POLL_INTERVAL}s)...")
        self.log("Press Ctrl+C to stop")

        try:
            while True:
                self.run_once()

                self.log(f"Sleeping for {POLL_INTERVAL} seconds...")
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            self.log("\nStopping watcher...", "INFO")
            self.log(f"Total emails processed this session: {self.processed_count}", "INFO")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gmail Inbox Watcher for AI Employee System"
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: do not mark emails as read'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run: do not create task files or mark as read'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Process emails once and exit (do not run continuously)'
    )

    args = parser.parse_args()

    # Banner
    print("=" * 70)
    print("Gmail Inbox Watcher for AI Employee System")
    print("=" * 70)
    print()

    if args.test:
        print("[TEST MODE] Emails will NOT be marked as read")
    if args.dry_run:
        print("[DRY RUN] No task files will be created, no emails marked as read")
    print()

    # Initialize watcher
    watcher = GmailWatcher(test_mode=args.test, dry_run=args.dry_run)

    # Authenticate
    if not watcher.authenticate():
        print("\n❌ Authentication failed. Exiting.")
        return 1

    print()

    # Run once or continuously
    if args.once:
        processed = watcher.run_once()
        print(f"\n✅ Processed {processed} email(s)")
        return 0
    else:
        watcher.run_continuous()
        return 0


if __name__ == "__main__":
    sys.exit(main())
