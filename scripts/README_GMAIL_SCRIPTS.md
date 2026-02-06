# Gmail OAuth Scripts - User Guide

This directory contains Python helper scripts for setting up Gmail OAuth2 authentication for the Gmail MCP Server.

## Quick Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup_gmail_oauth.py` | Interactive OAuth2 setup | First-time setup or re-authorization |
| `convert_gmail_token.py` | Format converter | After Python OAuth if Node.js server won't start |
| `test_setup.py` | Validate setup | Check if everything is configured correctly |

## Script Details

### 1. setup_gmail_oauth.py

**Purpose:** Complete OAuth2 authorization flow with browser interaction.

**What it does:**
- ✓ Validates your config.json exists and is correct
- ✓ Opens browser for Google consent screen
- ✓ Handles OAuth2 callback automatically
- ✓ Saves tokens to token.json
- ✓ Tests the token with Gmail API
- ✓ Provides detailed error messages

**Usage:**
```bash
python scripts/setup_gmail_oauth.py
```

**Interactive flow:**
1. Script checks for config.json
2. Opens browser to Google OAuth consent
3. You sign in and grant permissions
4. Script receives authorization code
5. Exchanges code for tokens
6. Saves token.json
7. Verifies token works

**Output:**
- Creates: `mcp_servers/email/token.json`
- Token format: Python (google-auth) format
- Includes: access_token, refresh_token, expiry

**Common Issues:**

*"Credentials file not found"*
- Download OAuth credentials from Google Cloud Console
- Save as `mcp_servers/email/config.json`

*"Port 8080 already in use"*
- Close applications using port 8080
- Or modify `REDIRECT_URI` in script (line 45)

*"Token verification failed"*
- Check Gmail API is enabled
- Verify all scopes were granted

### 2. convert_gmail_token.py

**Purpose:** Convert token format from Python to Node.js.

**Why needed:** The Python `google-auth` library and Node.js `googleapis` library use different JSON structures for tokens.

**What it does:**
- ✓ Loads Python-format token.json
- ✓ Creates backup (token.json.backup)
- ✓ Converts to Node.js format
- ✓ Validates expiry dates
- ✓ Preserves refresh token

**Usage:**
```bash
python scripts/convert_gmail_token.py
```

**Conversion details:**

**From (Python format):**
```json
{
  "token": "ya29.a0...",
  "refresh_token": "1//0g...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456.apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
  ],
  "expiry": "2024-02-05T14:30:00.000000Z"
}
```

**To (Node.js format):**
```json
{
  "access_token": "ya29.a0...",
  "refresh_token": "1//0g...",
  "scope": "https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.readonly",
  "token_type": "Bearer",
  "expiry_date": 1707143400000
}
```

**Key differences:**
- `token` → `access_token`
- `scopes` (array) → `scope` (space-separated string)
- `expiry` (ISO 8601) → `expiry_date` (Unix timestamp in ms)
- Adds `token_type: "Bearer"`

**When to use:**
- After running `setup_gmail_oauth.py`
- If Node.js server can't read token.json
- If you see "Invalid token format" errors

**Safety features:**
- Creates backup before conversion
- Confirms before overwriting
- Validates converted token

### 3. test_setup.py (in mcp_servers/email/)

**Purpose:** Validate that all setup steps are complete.

**What it checks:**
- ✓ config.json exists and is valid
- ✓ token.json exists and has correct format
- ✓ server.js and package.json present
- ✓ node_modules installed
- ✓ Required npm packages present
- ✓ Python dependencies (optional)

**Usage:**
```bash
cd mcp_servers/email
python test_setup.py
```

**Output example:**
```
==================================================================
  Gmail MCP Server Setup Validator
==================================================================

▶ Checking OAuth Credentials (config.json)
------------------------------------------------------------------
✓ config.json structure is valid
  Client ID: 123456789-abc123...
  Redirect URIs: 2 configured

▶ Checking OAuth Token (token.json)
------------------------------------------------------------------
✓ token.json found (Node.js format)
  Access Token: ya29.a0AfB_byABC123...
  Refresh Token: ✓ Present

▶ Checking Node.js Setup
------------------------------------------------------------------
✓ server.js: mcp_servers/email/server.js
✓ package.json: Valid JSON
✓ node_modules: Dependencies installed
✓ Required packages: All present

==================================================================
✓ All Required Checks Passed!
==================================================================

Your Gmail MCP server is ready to use!
```

**When to use:**
- Before starting the MCP server
- Troubleshooting setup issues
- After following setup guide
- Before asking for help

## Installation Requirements

### Python Dependencies

```bash
pip install -r scripts/requirements-gmail.txt
```

This installs:
- `google-auth-oauthlib` - OAuth2 flow handling
- `google-auth-httplib2` - Authenticated HTTP requests
- `google-api-python-client` - Gmail API client

**Note:** These are only needed for the Python setup scripts. The actual MCP server runs in Node.js.

### Node.js Dependencies

```bash
cd mcp_servers/email
npm install
```

This installs:
- `@modelcontextprotocol/sdk` - MCP protocol implementation
- `googleapis` - Gmail API for Node.js

## Complete Setup Flow

### Option A: Using Python Scripts (Recommended)

```bash
# 1. Install Python dependencies
pip install -r scripts/requirements-gmail.txt

# 2. Get config.json from Google Cloud Console
# (See SETUP_GUIDE.md for detailed instructions)

# 3. Run OAuth setup
python scripts/setup_gmail_oauth.py

# 4. Convert token format
python scripts/convert_gmail_token.py

# 5. Install Node.js dependencies
cd mcp_servers/email
npm install

# 6. Validate setup
python test_setup.py

# 7. Configure Claude for Desktop
# (Add to claude_desktop_config.json)

# 8. Start using in Claude!
```

### Option B: Using Node.js Only

```bash
# 1. Get config.json from Google Cloud Console

# 2. Install Node.js dependencies
cd mcp_servers/email
npm install

# 3. Run Node.js OAuth setup
node auth.js

# 4. Validate setup
python test_setup.py  # Optional

# 5. Configure Claude for Desktop

# 6. Start using in Claude!
```

## Troubleshooting

### Script won't run

**Windows:**
```bash
python scripts/setup_gmail_oauth.py
```

**macOS/Linux:**
```bash
python3 scripts/setup_gmail_oauth.py
# or
chmod +x scripts/setup_gmail_oauth.py
./scripts/setup_gmail_oauth.py
```

### Import errors

```
ModuleNotFoundError: No module named 'google.auth'
```

**Fix:**
```bash
pip install -r scripts/requirements-gmail.txt
```

### Browser doesn't open

The script will print a URL. Copy and paste it into your browser manually:
```
https://accounts.google.com/o/oauth2/auth?client_id=...
```

### "Invalid grant" error

Your authorization code expired or was already used.

**Fix:**
1. Delete token.json
2. Run the script again
3. Complete authorization within 10 minutes

### Token format issues

If you see errors about token format:

1. Check which format you have:
```bash
python -c "import json; print(json.load(open('mcp_servers/email/token.json'))['access_token' if 'access_token' in json.load(open('mcp_servers/email/token.json')) else 'token'][:20])"
```

2. Convert if needed:
```bash
python scripts/convert_gmail_token.py
```

## Security Best Practices

1. **Never commit credentials:**
   ```bash
   # Already in .gitignore:
   config.json
   token.json
   token.json.backup
   ```

2. **Use restrictive permissions:**
   ```bash
   chmod 600 mcp_servers/email/config.json
   chmod 600 mcp_servers/email/token.json
   ```

3. **OAuth consent screen:**
   - Use "External" type for testing
   - Add yourself as test user
   - Don't publish without proper review

4. **Token storage:**
   - Scripts automatically set 600 permissions
   - Tokens are stored locally only
   - Never transmitted except to Google

5. **Scope minimization:**
   - Only request scopes you need
   - Scripts request exactly 4 Gmail scopes
   - No access to other Google services

## File Locations

```
project/
├── scripts/
│   ├── setup_gmail_oauth.py    ← Main OAuth setup script
│   ├── convert_gmail_token.py  ← Token format converter
│   ├── requirements-gmail.txt  ← Python dependencies
│   └── README_GMAIL_SCRIPTS.md ← This file
│
└── mcp_servers/email/
    ├── config.json              ← OAuth credentials (from Google)
    ├── token.json               ← OAuth tokens (generated)
    ├── token.json.backup        ← Backup (if converted)
    ├── test_setup.py            ← Setup validator
    ├── server.js                ← MCP server
    ├── auth.js                  ← Alternative Node.js OAuth
    └── node_modules/            ← Node.js dependencies
```

## Support Resources

- **Setup Guide:** `mcp_servers/email/SETUP_GUIDE.md`
- **Quick Start:** `mcp_servers/email/QUICK_START.md`
- **Full Documentation:** `mcp_servers/email/README.md`
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Gmail API:** https://developers.google.com/gmail/api
- **OAuth2:** https://developers.google.com/identity/protocols/oauth2

## FAQ

**Q: Do I need both Python and Node.js?**
A: Python scripts are optional helpers. The actual MCP server requires Node.js. You can use Node.js `auth.js` instead of Python scripts.

**Q: Can I use my existing Google Cloud project?**
A: Yes! Just enable Gmail API and create OAuth credentials in your existing project.

**Q: How long does the token last?**
A: Access tokens expire in ~1 hour. Refresh tokens last indefinitely (until revoked). The server automatically refreshes tokens.

**Q: Is this secure?**
A: Yes, if you follow best practices:
- Keep config.json and token.json private
- Use 600 file permissions
- Don't commit to Git (already in .gitignore)
- Only grant to trusted applications

**Q: Can I automate this for CI/CD?**
A: For automation, use service accounts instead of OAuth2 user credentials. See Google Cloud documentation for service account setup.

**Q: What if I accidentally commit my credentials?**
A: Immediately:
1. Revoke the credentials in Google Cloud Console
2. Remove from Git history: `git filter-branch` or BFG Repo-Cleaner
3. Generate new credentials
4. Re-run setup scripts

## Contributing

Found a bug or have a suggestion? The scripts are designed to be:
- Clear and well-commented
- Error-tolerant with helpful messages
- Safe (backups, confirmations)
- Cross-platform compatible

Feel free to improve them!

---

**Last Updated:** February 2026
**Python Version:** 3.10+
**Node.js Version:** 16+
