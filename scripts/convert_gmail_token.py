#!/usr/bin/env python3
"""
Gmail Token Format Converter

Converts the token.json format from Python OAuth2 format to Node.js googleapis format.
The two libraries use slightly different JSON structures for storing OAuth2 tokens.

Python format (google-auth):
{
  "token": "access_token_value",
  "refresh_token": "refresh_token_value",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "client_id_value",
  "client_secret": "client_secret_value",
  "scopes": ["scope1", "scope2"],
  "expiry": "2024-02-05T12:00:00.000000Z"
}

Node.js format (googleapis):
{
  "access_token": "access_token_value",
  "refresh_token": "refresh_token_value",
  "scope": "scope1 scope2",
  "token_type": "Bearer",
  "expiry_date": 1707134400000
}

Usage:
    python scripts/convert_gmail_token.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_TOKEN_PATH = PROJECT_ROOT / "mcp_servers" / "email" / "token.json"
NODEJS_TOKEN_PATH = PROJECT_ROOT / "mcp_servers" / "email" / "token.json"
BACKUP_PATH = PROJECT_ROOT / "mcp_servers" / "email" / "token.json.backup"


def print_header():
    """Print script header."""
    print("=" * 70)
    print("  Gmail Token Format Converter")
    print("  Python (google-auth) → Node.js (googleapis)")
    print("=" * 70)
    print()


def load_python_token():
    """
    Load and validate Python-format token.

    Returns:
        dict: Token data in Python format
    """
    if not PYTHON_TOKEN_PATH.exists():
        print(f"❌ Error: Token file not found at {PYTHON_TOKEN_PATH}")
        print()
        print("Please run the OAuth setup first:")
        print("  python scripts/setup_gmail_oauth.py")
        return None

    try:
        with open(PYTHON_TOKEN_PATH, 'r', encoding='utf-8') as f:
            token_data = json.load(f)

        # Check if it's Python format
        if 'token' in token_data:
            print("✓ Found Python-format token")
            return token_data
        elif 'access_token' in token_data:
            print("ℹ️  Token is already in Node.js format")
            return None
        else:
            print("❌ Error: Unknown token format")
            return None

    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {PYTHON_TOKEN_PATH}")
        return None
    except Exception as e:
        print(f"❌ Error reading token: {e}")
        return None


def convert_expiry_to_timestamp(expiry_str):
    """
    Convert ISO 8601 datetime string to Unix timestamp in milliseconds.

    Args:
        expiry_str (str): ISO 8601 datetime string

    Returns:
        int: Unix timestamp in milliseconds
    """
    try:
        # Parse ISO 8601 datetime
        # Handle both with and without timezone
        if expiry_str.endswith('Z'):
            dt = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(expiry_str)

        # Convert to Unix timestamp in milliseconds
        timestamp = int(dt.timestamp() * 1000)
        return timestamp
    except Exception as e:
        print(f"⚠️  Warning: Could not parse expiry date: {e}")
        # Return timestamp for 1 hour from now as fallback
        from datetime import datetime, timedelta
        return int((datetime.utcnow() + timedelta(hours=1)).timestamp() * 1000)


def convert_token(python_token):
    """
    Convert Python-format token to Node.js format.

    Args:
        python_token (dict): Token in Python format

    Returns:
        dict: Token in Node.js format
    """
    print("\n▶ Converting token format...")
    print("-" * 70)

    # Extract values from Python format
    access_token = python_token.get('token')
    refresh_token = python_token.get('refresh_token')
    scopes = python_token.get('scopes', [])
    expiry = python_token.get('expiry')

    # Validate required fields
    if not access_token:
        print("❌ Error: No access token found")
        return None

    if not refresh_token:
        print("⚠️  Warning: No refresh token found (token will expire)")

    # Convert to Node.js format
    nodejs_token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "scope": " ".join(scopes),  # Space-separated instead of array
        "token_type": "Bearer",
        "expiry_date": convert_expiry_to_timestamp(expiry) if expiry else None
    }

    # Print conversion details
    print("\nConverted fields:")
    print(f"  token → access_token: {access_token[:20]}...")
    print(f"  refresh_token: {'✓ Present' if refresh_token else '✗ Missing'}")
    print(f"  scopes → scope: {len(scopes)} scopes")
    print(f"  expiry → expiry_date: {nodejs_token['expiry_date']}")

    return nodejs_token


def backup_token():
    """Create a backup of the existing token file."""
    if PYTHON_TOKEN_PATH.exists():
        try:
            with open(PYTHON_TOKEN_PATH, 'r', encoding='utf-8') as f:
                backup_data = f.read()

            with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
                f.write(backup_data)

            print(f"✓ Backup created: {BACKUP_PATH}")
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
            return False
    return True


def save_nodejs_token(nodejs_token):
    """
    Save the Node.js format token.

    Args:
        nodejs_token (dict): Token in Node.js format
    """
    try:
        with open(NODEJS_TOKEN_PATH, 'w', encoding='utf-8') as f:
            json.dump(nodejs_token, f, indent=2)

        print(f"\n✓ Saved Node.js format token to: {NODEJS_TOKEN_PATH}")
        return True
    except Exception as e:
        print(f"\n❌ Error saving token: {e}")
        return False


def print_summary():
    """Print summary and next steps."""
    print("\n" + "=" * 70)
    print("✓ Token conversion completed successfully!")
    print("=" * 70)
    print()

    print("Next Steps:")
    print()
    print("1. Test the MCP server:")
    print("   cd mcp_servers/email")
    print("   node server.js")
    print()
    print("2. Configure Claude for Desktop:")
    print('   Add to claude_desktop_config.json:')
    print()
    print("   {")
    print('     "mcpServers": {')
    print('       "gmail": {')
    print('         "command": "node",')
    print('         "args": ["/absolute/path/to/mcp_servers/email/server.js"]')
    print('       }')
    print('     }')
    print("   }")
    print()
    print("3. Restart Claude for Desktop completely (Cmd+Q on macOS)")
    print()
    print("4. Test in Claude:")
    print('   "Search my Gmail for unread emails"')
    print()


def main():
    """Main conversion function."""
    print_header()

    # Load Python token
    print("▶ Step 1: Loading Python-format token")
    print("-" * 70)
    python_token = load_python_token()

    if not python_token:
        print("\nNo conversion needed or token not found.")
        return

    # Create backup
    print("\n▶ Step 2: Creating backup")
    print("-" * 70)
    backup_token()

    # Convert format
    nodejs_token = convert_token(python_token)

    if not nodejs_token:
        print("\n❌ Conversion failed")
        return

    # Confirm before overwriting
    print("\n▶ Step 3: Saving converted token")
    print("-" * 70)
    response = input("\nOverwrite token.json with Node.js format? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\n❌ Conversion cancelled")
        print(f"ℹ️  Backup is available at: {BACKUP_PATH}")
        return

    # Save Node.js format
    if save_nodejs_token(nodejs_token):
        print_summary()
    else:
        print("\n❌ Failed to save token")
        print(f"ℹ️  Backup is available at: {BACKUP_PATH}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Conversion cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
