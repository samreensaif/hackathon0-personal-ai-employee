#!/usr/bin/env python3
"""
Approval Template Generator

Generates approval request files from templates with variable substitution.
Used by task processors to create properly formatted approval requests.

Usage:
    # Generate email approval
    python scripts/generate_approval.py email \\
        --to "client@example.com" \\
        --subject "Invoice for January" \\
        --body "Please find attached..." \\
        --output "AI_Employee_Vault/Pending_Approval/invoice_email.md"

    # Generate draft approval
    python scripts/generate_approval.py draft \\
        --to "team@company.com" \\
        --subject "Weekly Report" \\
        --body "Report content..." \\
        --output "AI_Employee_Vault/Pending_Approval/weekly_draft.md"

    # Generate search approval
    python scripts/generate_approval.py search \\
        --query "from:boss@company.com is:unread" \\
        --max-results 10 \\
        --output "AI_Employee_Vault/Pending_Approval/search_boss.md"
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import re

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
VAULT_PATH = PROJECT_ROOT / "AI_Employee_Vault"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"

# Template files
TEMPLATES = {
    'email': TEMPLATES_DIR / "approval_email.md",
    'draft': TEMPLATES_DIR / "approval_draft.md",
    'search': TEMPLATES_DIR / "approval_search.md",
}

# Default expiry times
DEFAULT_EXPIRY_HOURS = {
    'email': 48,    # 2 days
    'draft': 72,    # 3 days
    'search': 24,   # 1 day
}


# =============================================================================
# TEMPLATE PROCESSOR
# =============================================================================

class ApprovalTemplateGenerator:
    """
    Generates approval request files from templates.

    Handles variable substitution and validation.
    """

    def __init__(self, template_type: str):
        """
        Initialize generator.

        Args:
            template_type: Type of approval (email, draft, search)

        Raises:
            ValueError: If template type is not supported
        """
        if template_type not in TEMPLATES:
            raise ValueError(f"Unknown template type: {template_type}")

        self.template_type = template_type
        self.template_path = TEMPLATES[template_type]

        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

    def generate(
        self,
        variables: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate approval request from template.

        Args:
            variables: Variables for substitution
            output_path: Optional output file path

        Returns:
            Generated content

        Raises:
            ValueError: If required variables are missing
        """
        # Load template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Add default variables
        variables = self._add_defaults(variables)

        # Validate required variables
        self._validate_variables(variables)

        # Substitute variables
        content = self._substitute_variables(template, variables)

        # Write to file if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Generated approval request: {output_path}")

        return content

    def _add_defaults(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Add default variables."""
        now = datetime.now()

        defaults = {
            'CREATED_TIMESTAMP': now.isoformat() + 'Z',
            'EXPIRES_TIMESTAMP': (
                now + timedelta(hours=DEFAULT_EXPIRY_HOURS[self.template_type])
            ).isoformat() + 'Z',
            'PRIORITY_LEVEL': 'medium',
            'APPROVAL_REASON': 'Requires human review',
            'ORIGINAL_TASK_FILE': 'unknown',
            'TASK_PRIORITY': 'normal',
            'TASK_CATEGORY': 'general',
            'EMAIL_CC': '',
            'ATTACHMENT_PATH_1': '',
            'ATTACHMENT_NAME_1': '',
            'ATTACHMENT_MIME_TYPE_1': '',
            'CURRENT_RATE_LIMIT_USAGE': '0',
            'TIME_REMAINING': self._calculate_time_remaining(
                DEFAULT_EXPIRY_HOURS[self.template_type]
            ),
            'FILE_NAME': variables.get('output_filename', 'approval_request.md'),
        }

        # Merge with provided variables (provided takes precedence)
        return {**defaults, **variables}

    def _validate_variables(self, variables: Dict[str, Any]):
        """
        Validate that required variables are present.

        Raises:
            ValueError: If required variables are missing
        """
        required = {
            'email': ['RECIPIENT_EMAIL', 'EMAIL_SUBJECT', 'EMAIL_BODY'],
            'draft': ['RECIPIENT_EMAIL', 'EMAIL_SUBJECT', 'EMAIL_BODY'],
            'search': ['SEARCH_QUERY', 'MAX_RESULTS'],
        }

        required_vars = required[self.template_type]

        missing = [var for var in required_vars if var not in variables]

        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in template.

        Supports:
        - {{VARIABLE}} - Simple substitution
        - {{#if VARIABLE}}...{{/if}} - Conditional blocks (simple implementation)

        Args:
            template: Template content
            variables: Variables dict

        Returns:
            Content with variables substituted
        """
        content = template

        # Simple variable substitution
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        # Handle conditional blocks (simplified implementation)
        # Remove {{#if VAR}}...{{/if}} blocks where VAR is empty
        def replace_conditional(match):
            var_name = match.group(1)
            inner_content = match.group(2)

            # Check if variable exists and is truthy
            if var_name in variables and variables[var_name]:
                return inner_content
            else:
                return ''

        content = re.sub(
            r'\{\{#if ([A-Z_]+)\}\}(.*?)\{\{/if\}\}',
            replace_conditional,
            content,
            flags=re.DOTALL
        )

        # Handle {{#each}} blocks (simplified - just remove for now)
        content = re.sub(
            r'\{\{#each [A-Z_]+\}\}(.*?)\{\{/each\}\}',
            '',
            content,
            flags=re.DOTALL
        )

        # Create body preview (first 100 chars)
        if 'EMAIL_BODY' in variables:
            body = variables['EMAIL_BODY']
            preview = body[:100] + ('...' if len(body) > 100 else '')
            content = content.replace('{{BODY_PREVIEW_100_CHARS}}', preview)

        return content

    def _calculate_time_remaining(self, hours: int) -> str:
        """Calculate human-readable time remaining."""
        if hours >= 48:
            days = hours // 24
            return f"{days} days"
        elif hours >= 24:
            return "1 day"
        else:
            return f"{hours} hours"


# =============================================================================
# CLI INTERFACE
# =============================================================================

def generate_email_approval(args):
    """Generate email send approval request."""
    generator = ApprovalTemplateGenerator('email')

    variables = {
        'RECIPIENT_EMAIL': args.to,
        'EMAIL_SUBJECT': args.subject,
        'EMAIL_BODY': args.body,
        'EMAIL_BODY_FULL': args.body,
        'EMAIL_CC': args.cc or '',
        'PRIORITY_LEVEL': args.priority or 'medium',
        'ORIGINAL_TASK_FILE': args.task or 'manual_request',
        'APPROVAL_REASON': args.reason or 'Email action requires approval',
    }

    # Add attachment info if provided
    if args.attachment:
        variables['ATTACHMENT_PATH_1'] = args.attachment
        variables['ATTACHMENT_NAME_1'] = Path(args.attachment).name
        variables['ATTACHMENT_MIME_TYPE_1'] = 'application/pdf'

    output_path = Path(args.output) if args.output else None
    content = generator.generate(variables, output_path)

    if not output_path:
        print(content)


def generate_draft_approval(args):
    """Generate draft email approval request."""
    generator = ApprovalTemplateGenerator('draft')

    variables = {
        'RECIPIENT_EMAIL': args.to,
        'EMAIL_SUBJECT': args.subject,
        'EMAIL_BODY': args.body,
        'EMAIL_BODY_FULL': args.body,
        'ORIGINAL_TASK_FILE': args.task or 'manual_request',
        'APPROVAL_REASON': args.reason or 'Draft creation requires review',
    }

    output_path = Path(args.output) if args.output else None
    content = generator.generate(variables, output_path)

    if not output_path:
        print(content)


def generate_search_approval(args):
    """Generate email search approval request."""
    generator = ApprovalTemplateGenerator('search')

    variables = {
        'SEARCH_QUERY': args.query,
        'MAX_RESULTS': str(args.max_results),
        'QUERY_EXPLANATION': _explain_query(args.query),
        'ORIGINAL_TASK_FILE': args.task or 'manual_request',
        'APPROVAL_REASON': args.reason or 'Email search requires approval',
    }

    output_path = Path(args.output) if args.output else None
    content = generator.generate(variables, output_path)

    if not output_path:
        print(content)


def _explain_query(query: str) -> str:
    """Generate human-readable explanation of Gmail query."""
    explanations = []

    if 'from:' in query:
        sender = re.search(r'from:(\S+)', query)
        if sender:
            explanations.append(f"From {sender.group(1)}")

    if 'to:' in query:
        recipient = re.search(r'to:(\S+)', query)
        if recipient:
            explanations.append(f"To {recipient.group(1)}")

    if 'subject:' in query:
        subject = re.search(r'subject:(\S+)', query)
        if subject:
            explanations.append(f"Subject contains '{subject.group(1)}'")

    if 'is:unread' in query:
        explanations.append("Unread only")

    if 'is:important' in query:
        explanations.append("Important only")

    if 'has:attachment' in query:
        explanations.append("Has attachments")

    return "Searching for: " + ", ".join(explanations) if explanations else query


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate approval request files from templates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate email approval
  python scripts/generate_approval.py email \\
      --to client@example.com \\
      --subject "Invoice" \\
      --body "Please find attached..." \\
      --output AI_Employee_Vault/Pending_Approval/invoice.md

  # Generate draft approval
  python scripts/generate_approval.py draft \\
      --to team@company.com \\
      --subject "Weekly Report" \\
      --body "Report content"

  # Generate search approval
  python scripts/generate_approval.py search \\
      --query "from:boss@company.com" \\
      --max-results 10
        """
    )

    # Subcommands for different approval types
    subparsers = parser.add_subparsers(dest='command', help='Approval type')

    # Email approval
    email_parser = subparsers.add_parser('email', help='Generate email send approval')
    email_parser.add_argument('--to', required=True, help='Recipient email address')
    email_parser.add_argument('--subject', required=True, help='Email subject')
    email_parser.add_argument('--body', required=True, help='Email body content')
    email_parser.add_argument('--cc', help='CC email address')
    email_parser.add_argument('--attachment', help='Attachment file path')
    email_parser.add_argument('--priority', choices=['low', 'medium', 'high'], help='Priority level')
    email_parser.add_argument('--task', help='Original task file name')
    email_parser.add_argument('--reason', help='Reason for approval requirement')
    email_parser.add_argument('--output', help='Output file path')

    # Draft approval
    draft_parser = subparsers.add_parser('draft', help='Generate draft email approval')
    draft_parser.add_argument('--to', required=True, help='Recipient email address')
    draft_parser.add_argument('--subject', required=True, help='Email subject')
    draft_parser.add_argument('--body', required=True, help='Email body content')
    draft_parser.add_argument('--task', help='Original task file name')
    draft_parser.add_argument('--reason', help='Reason for approval requirement')
    draft_parser.add_argument('--output', help='Output file path')

    # Search approval
    search_parser = subparsers.add_parser('search', help='Generate email search approval')
    search_parser.add_argument('--query', required=True, help='Gmail search query')
    search_parser.add_argument('--max-results', type=int, default=10, help='Max results (default: 10)')
    search_parser.add_argument('--task', help='Original task file name')
    search_parser.add_argument('--reason', help='Reason for approval requirement')
    search_parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'email':
            generate_email_approval(args)
        elif args.command == 'draft':
            generate_draft_approval(args)
        elif args.command == 'search':
            generate_search_approval(args)
        else:
            print(f"Error: Unknown command '{args.command}'")
            sys.exit(1)

        print("[OK] Approval request generated successfully")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
