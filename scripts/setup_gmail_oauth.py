#!/usr/bin/env python3
"""
Gmail OAuth2 Setup Script

This script helps you authenticate with the Gmail API by running an interactive
OAuth2 flow. It will open your browser for consent and save the tokens needed
by the Gmail MCP server.

Usage:
    python scripts/setup_gmail_oauth.py

Requirements:
    - google-auth-oauthlib
    - google-auth-httplib2
    - google-api-python-client

Install with:
    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import json
import os
import sys
from pathlib import Path

# Try to import required Google libraries
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError as e:
    print("❌ Error: Required Google libraries not found.")
    print("\nPlease install them with:")
    print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print(f"\nMissing module: {e.name}")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Gmail API scopes required for the MCP server
# These scopes determine what the application can do with Gmail
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',      # Send emails
    'https://www.googleapis.com/auth/gmail.compose',   # Create and manage drafts
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails and search
    'https://www.googleapis.com/auth/gmail.modify'     # Modify emails (for drafts)
]

# Define paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
CREDENTIALS_PATH = PROJECT_ROOT / "mcp_servers" / "email" / "config.json"
TOKEN_PATH = PROJECT_ROOT / "mcp_servers" / "email" / "token.json"

# OAuth2 redirect URI - localhost for desktop apps
REDIRECT_URI = "http://localhost:8080/"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_header():
    """Print a nice header for the script."""
    print("=" * 70)
    print("  Gmail OAuth2 Setup for MCP Server")
    print("=" * 70)
    print()


def print_section(title):
    """Print a section divider."""
    print()
    print(f"▶ {title}")
    print("-" * 70)


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")


def print_warning(message):
    """Print a warning message."""
    print(f"⚠️  {message}")


def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")


def check_credentials_file():
    """
    Check if the credentials file (config.json) exists.

    Returns:
        bool: True if credentials file exists and is valid, False otherwise
    """
    if not CREDENTIALS_PATH.exists():
        print_error("Credentials file not found!")
        print()
        print(f"Expected location: {CREDENTIALS_PATH}")
        print()
        print("📋 How to get your credentials:")
        print()
        print("1. Go to Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print()
        print("2. Create a new project or select an existing one")
        print()
        print("3. Enable the Gmail API:")
        print("   - Navigate to: APIs & Services > Library")
        print("   - Search for 'Gmail API'")
        print("   - Click 'Enable'")
        print()
        print("4. Configure OAuth Consent Screen:")
        print("   - Navigate to: APIs & Services > OAuth consent screen")
        print("   - User Type: Select 'External' (for testing)")
        print("   - Fill in required fields:")
        print("     * App name: Gmail MCP Server")
        print("     * User support email: your email")
        print("     * Developer contact: your email")
        print("   - Add test users: your Gmail address")
        print()
        print("5. Create OAuth2 Credentials:")
        print("   - Navigate to: APIs & Services > Credentials")
        print("   - Click: Create Credentials > OAuth client ID")
        print("   - Application type: Desktop app")
        print("   - Name: Gmail MCP Server")
        print("   - Click 'Create'")
        print()
        print("6. Download the credentials:")
        print("   - Click the download button (⬇) for your new OAuth client")
        print("   - Save the downloaded JSON file as:")
        print(f"     {CREDENTIALS_PATH}")
        print()
        return False

    # Validate the credentials file format
    try:
        with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
            creds_data = json.load(f)

        # Check for valid credential structure
        if 'installed' not in creds_data and 'web' not in creds_data:
            print_error("Invalid credentials file format!")
            print()
            print("The config.json file must contain either 'installed' or 'web' credentials.")
            print("Please download the correct OAuth2 credentials from Google Cloud Console.")
            return False

        print_success(f"Found credentials file: {CREDENTIALS_PATH}")
        return True

    except json.JSONDecodeError:
        print_error("Credentials file is not valid JSON!")
        print()
        print(f"Please check the file: {CREDENTIALS_PATH}")
        return False
    except Exception as e:
        print_error(f"Error reading credentials file: {e}")
        return False


def get_existing_token():
    """
    Check if a valid token already exists.

    Returns:
        Credentials or None: Valid credentials if token exists and is valid, None otherwise
    """
    if not TOKEN_PATH.exists():
        return None

    try:
        # Load existing credentials from token file
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        # Check if credentials are valid
        if creds and creds.valid:
            print_success("Found valid existing token")
            return creds

        # If credentials expired but have refresh token, try to refresh
        if creds and creds.expired and creds.refresh_token:
            print_info("Token expired, attempting to refresh...")
            try:
                creds.refresh(Request())
                print_success("Token refreshed successfully")
                return creds
            except Exception as e:
                print_warning(f"Failed to refresh token: {e}")
                return None

        return None

    except Exception as e:
        print_warning(f"Could not load existing token: {e}")
        return None


def run_oauth_flow():
    """
    Run the interactive OAuth2 authorization flow.

    This function:
    1. Creates an OAuth2 flow using the credentials file
    2. Starts a local server to receive the authorization response
    3. Opens the user's browser to the Google consent screen
    4. Waits for the user to authorize the application
    5. Exchanges the authorization code for tokens

    Returns:
        Credentials: The authorized credentials with access and refresh tokens
    """
    print_section("Starting OAuth2 Authorization Flow")
    print()
    print("Steps that will happen:")
    print("  1. Your default browser will open")
    print("  2. Sign in to your Google account")
    print("  3. Grant permissions to the application")
    print("  4. The browser will redirect back (you can close it after)")
    print("  5. Tokens will be saved automatically")
    print()

    # Ask user if ready to proceed
    response = input("Ready to proceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print()
        print_info("Authorization cancelled. Run the script again when ready.")
        sys.exit(0)

    try:
        # Create the OAuth2 flow from the credentials file
        # This flow will handle the entire authorization process
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_PATH),
            SCOPES,
            redirect_uri=REDIRECT_URI
        )

        # Run the local server to handle the OAuth callback
        # This will:
        # - Start a temporary web server on localhost:8080
        # - Open the browser to Google's authorization page
        # - Wait for the authorization response
        # - Exchange the authorization code for access/refresh tokens
        print()
        print_info("Opening browser for authorization...")
        print_info("If browser doesn't open, copy the URL from the terminal")
        print()

        creds = flow.run_local_server(
            port=8080,
            success_message="Authorization successful! You can close this window.",
            open_browser=True
        )

        print()
        print_success("Authorization completed successfully!")
        return creds

    except Exception as e:
        print()
        print_error(f"Authorization failed: {e}")
        print()
        print("Common issues:")
        print("  - Port 8080 is already in use (try closing other applications)")
        print("  - Browser popup was blocked (check your browser settings)")
        print("  - Credentials file is invalid (re-download from Google Cloud)")
        sys.exit(1)


def save_token(creds):
    """
    Save the credentials to the token file.

    Args:
        creds (Credentials): The credentials object to save
    """
    try:
        # Ensure the directory exists
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Save credentials to file in JSON format
        # This file will contain:
        # - access_token: Short-lived token for API requests
        # - refresh_token: Long-lived token to get new access tokens
        # - token_uri: Google's token endpoint
        # - client_id: Your OAuth client ID
        # - client_secret: Your OAuth client secret
        # - scopes: The scopes this token is valid for
        with open(TOKEN_PATH, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())

        # Set restrictive permissions on the token file for security
        # This makes the file readable/writable only by the owner
        os.chmod(TOKEN_PATH, 0o600)

        print_success(f"Token saved to: {TOKEN_PATH}")
        print_info(f"File permissions set to 600 (owner read/write only)")

    except Exception as e:
        print_error(f"Failed to save token: {e}")
        sys.exit(1)


def verify_token(creds):
    """
    Verify the token works by making a test API call.

    Args:
        creds (Credentials): The credentials to verify

    Returns:
        bool: True if token is valid and API works, False otherwise
    """
    print_section("Verifying Token")

    try:
        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Make a simple API call to get user profile
        # This verifies:
        # - Token is valid
        # - Gmail API is accessible
        # - Scopes are sufficient
        profile = service.users().getProfile(userId='me').execute()

        email_address = profile.get('emailAddress', 'Unknown')
        print_success(f"Successfully connected to Gmail API")
        print_info(f"Authenticated as: {email_address}")
        print_info(f"Messages in mailbox: {profile.get('messagesTotal', 0):,}")
        print_info(f"Threads in mailbox: {profile.get('threadsTotal', 0):,}")

        return True

    except Exception as e:
        print_error(f"Token verification failed: {e}")
        print()
        print("This could mean:")
        print("  - Gmail API is not enabled in your Google Cloud project")
        print("  - The token scopes are insufficient")
        print("  - Network connectivity issues")
        return False


def print_summary(creds):
    """
    Print a summary of the authentication status.

    Args:
        creds (Credentials): The credentials to summarize
    """
    print_section("Summary")
    print()

    # Extract token information
    print("Token Information:")
    print(f"  ✓ Access Token: {creds.token[:20]}..." if creds.token else "  ✗ No access token")
    print(f"  ✓ Refresh Token: {'Present' if creds.refresh_token else 'Missing (will expire!)'}")
    print(f"  ✓ Expiry: {creds.expiry.strftime('%Y-%m-%d %H:%M:%S') if creds.expiry else 'Unknown'}")
    print()

    print("Granted Scopes:")
    for scope in SCOPES:
        scope_name = scope.split('/')[-1]
        print(f"  ✓ {scope_name}")
    print()

    print("Configuration Files:")
    print(f"  ✓ Credentials: {CREDENTIALS_PATH}")
    print(f"  ✓ Token: {TOKEN_PATH}")
    print()

    # Warn if no refresh token
    if not creds.refresh_token:
        print_warning("No refresh token received!")
        print()
        print("This means the token will expire and cannot be refreshed automatically.")
        print("To fix this:")
        print("  1. Go to: https://myaccount.google.com/permissions")
        print("  2. Remove 'Gmail MCP Server' from the list")
        print("  3. Run this script again")
        print()


def print_next_steps():
    """Print instructions for using the token with the MCP server."""
    print_section("Next Steps")
    print()

    print("1. Convert token format for Node.js MCP server:")
    print()
    print("   The Python token format needs to be converted.")
    print("   Run the Node.js auth script:")
    print()
    print("   cd mcp_servers/email")
    print("   node auth.js")
    print()
    print("   OR manually convert token.json to Node.js format:")
    print()
    print("   {")
    print('     "access_token": "your_access_token",')
    print('     "refresh_token": "your_refresh_token",')
    print('     "scope": "space separated scopes",')
    print('     "token_type": "Bearer",')
    print('     "expiry_date": unix_timestamp_in_milliseconds')
    print("   }")
    print()

    print("2. Configure Claude for Desktop:")
    print()
    print('   Add to ~/Library/Application Support/Claude/claude_desktop_config.json')
    print('   (or %APPDATA%\\Claude\\claude_desktop_config.json on Windows):')
    print()
    print("   {")
    print('     "mcpServers": {')
    print('       "gmail": {')
    print('         "command": "node",')
    print('         "args": [')
    print('           "/absolute/path/to/mcp_servers/email/server.js"')
    print('         ]')
    print('       }')
    print('     }')
    print("   }")
    print()

    print("3. Restart Claude for Desktop:")
    print()
    print("   - macOS: Press Cmd+Q to fully quit")
    print("   - Windows: Right-click system tray icon > Quit")
    print("   - Then reopen Claude for Desktop")
    print()

    print("4. Test in Claude:")
    print()
    print('   Try: "Search my Gmail for unread emails"')
    print('   Try: "Draft an email to test@example.com"')
    print()


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """
    Main function that orchestrates the OAuth2 setup process.

    Flow:
    1. Check if credentials file exists
    2. Check if valid token already exists
    3. If needed, run OAuth flow
    4. Save token to file
    5. Verify token works
    6. Print summary and next steps
    """
    print_header()

    # Step 1: Check for credentials file
    print_section("Step 1: Checking Credentials File")
    if not check_credentials_file():
        sys.exit(1)
    print()

    # Step 2: Check for existing valid token
    print_section("Step 2: Checking Existing Token")
    creds = get_existing_token()

    if creds:
        print()
        response = input("Valid token exists. Do you want to re-authorize? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print_info("Using existing token")
        else:
            print_info("Will create new token")
            creds = None
    else:
        print_info("No valid token found, authorization required")
    print()

    # Step 3: Run OAuth flow if needed
    if not creds:
        creds = run_oauth_flow()

        # Step 4: Save the token
        print_section("Step 3: Saving Token")
        save_token(creds)
        print()

    # Step 5: Verify the token
    if not verify_token(creds):
        print_warning("Token verification failed, but token was saved")
        print_info("You can try using it anyway")
        print()
    else:
        print()

    # Step 6: Print summary
    print_summary(creds)

    # Step 7: Print next steps
    print_next_steps()

    # Final success message
    print("=" * 70)
    print_success("Gmail OAuth2 setup completed!")
    print("=" * 70)
    print()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print_info("Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        print()
        print("If this error persists, please check:")
        print("  - Your internet connection")
        print("  - Google Cloud Console settings")
        print("  - That all required Python packages are installed")
        sys.exit(1)
