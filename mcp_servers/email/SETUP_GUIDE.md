# Gmail MCP Server - Quick Setup Guide

This guide will walk you through setting up the Gmail MCP Server step-by-step.

## Prerequisites Checklist

- [ ] Node.js 16+ installed (`node --version`)
- [ ] A Google account with Gmail
- [ ] Claude for Desktop installed (latest version)

## Setup Steps

### 1. Install Dependencies (2 minutes)

```bash
cd mcp_servers/email
npm install
```

### 2. Get Google Cloud Credentials (10 minutes)

#### 2.1 Create Google Cloud Project

1. Visit: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name: "Gmail MCP Server"
4. Click "Create"

#### 2.2 Enable Gmail API

1. In the project, go to: "APIs & Services" → "Library"
2. Search for: "Gmail API"
3. Click "Enable"

#### 2.3 Configure OAuth Consent Screen

1. Go to: "APIs & Services" → "OAuth consent screen"
2. User Type: Select "External"
3. Click "Create"
4. Fill in:
   - App name: "Gmail MCP Server"
   - User support email: your email
   - Developer contact: your email
5. Click "Save and Continue"
6. Scopes: Click "Add or Remove Scopes"
   - Add these scopes:
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.compose`
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.modify`
7. Click "Save and Continue"
8. Test users: Add your Gmail address
9. Click "Save and Continue"

#### 2.4 Create OAuth Credentials

1. Go to: "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Gmail MCP Server"
5. Click "Create"
6. Click "Download JSON" (download button)
7. Rename the file to `config.json`
8. Move it to: `mcp_servers/email/config.json`

### 3. Authorize the Application (2 minutes)

```bash
node auth.js
```

Follow these steps:
1. A URL will be displayed - copy and open it in your browser
2. Sign in with your Google account
3. Click "Continue" (you may see a warning - this is normal for testing)
4. Grant the requested permissions
5. Copy the authorization code
6. Paste it into the terminal
7. Press Enter

You should see: `✓ Success! Token has been saved to token.json`

### 4. Test the Server (1 minute)

Test standalone:
```bash
node server.js
```

You should see: `[INFO] Gmail MCP Server is running on stdio`

Press Ctrl+C to stop.

### 5. Configure Claude for Desktop (2 minutes)

#### macOS:
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Windows:
```powershell
code %APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration (replace with your actual path):

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": [
        "/ABSOLUTE/PATH/TO/mcp_servers/email/server.js"
      ]
    }
  }
}
```

**Important:** Use absolute paths! Get it with:
- macOS/Linux: `pwd` (run in the email directory)
- Windows: `cd` (run in the email directory)

### 6. Restart Claude for Desktop

**Critical:** Fully quit Claude (don't just close the window)
- macOS: Press Cmd+Q
- Windows: Right-click system tray icon → "Quit"

Then reopen Claude for Desktop.

### 7. Verify Installation

In Claude for Desktop:
1. Look for the 📎 icon in the input area
2. Click it and hover over "Connectors"
3. You should see "gmail" listed with 3 tools:
   - send_email
   - draft_email
   - search_emails

### 8. Test with Commands

Try these in Claude:

**Search emails:**
```
Search my Gmail for unread emails from the last week
```

**Draft an email:**
```
Draft an email to test@example.com with subject "Test" saying hello
```

**Send an email (to yourself):**
```
Send an email to [your-email] with subject "MCP Test" and body "This is a test from the Gmail MCP Server"
```

## Troubleshooting

### Server not showing in Claude

**Check logs:**
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp.log

# Windows
type %APPDATA%\Claude\logs\mcp.log
```

**Common fixes:**
1. Verify absolute path in config
2. Ensure Node.js is in PATH: `which node` (macOS) or `where node` (Windows)
3. Check file permissions: `chmod +x server.js` (macOS/Linux)
4. Fully restart Claude (Cmd+Q on macOS)

### Authentication errors

**"Could not load token.json":**
- Run: `node auth.js`
- Follow authorization steps again

**"invalid_grant" error:**
1. Delete `token.json`
2. Run `node auth.js` again
3. Make sure you're using the same Google account

**"Access token expired":**
- This should auto-refresh, but if it fails:
- Delete `token.json`
- Run `node auth.js`

### Gmail API errors

**"Insufficient Permission":**
- Re-run: `node auth.js`
- Ensure all 4 scopes are granted during authorization

**"User Rate Limit Exceeded":**
- Wait a few minutes
- Gmail has daily sending limits (100-500 emails/day)

**"Backend Error":**
- Try again in a few minutes
- Check Gmail API status: https://status.cloud.google.com/

## Security Notes

- ✅ `config.json` contains your OAuth client secret - DO NOT SHARE
- ✅ `token.json` contains your access token - DO NOT COMMIT TO GIT
- ✅ `.gitignore` is configured to exclude these files
- ✅ For production, configure OAuth consent screen properly
- ✅ Only grant minimum required scopes

## File Checklist

After setup, you should have:

```
mcp_servers/email/
├── server.js          ✅ Main server (provided)
├── auth.js            ✅ Auth helper (provided)
├── package.json       ✅ Dependencies (provided)
├── config.json        ⚠️  Your OAuth credentials (DO NOT COMMIT)
├── token.json         ⚠️  Your access token (DO NOT COMMIT)
├── node_modules/      ✅ Dependencies (auto-generated)
├── README.md          ✅ Full documentation
├── SETUP_GUIDE.md     ✅ This guide
└── .gitignore         ✅ Protects secrets
```

## Next Steps

Once everything is working:

1. **Test all features:**
   - Send email to yourself
   - Create a few drafts
   - Search your emails

2. **Read the full README.md** for:
   - Advanced search queries
   - Attachment handling
   - Production deployment tips

3. **Integrate with your workflow:**
   - Use with the AI Employee system
   - Automate email responses
   - Search and categorize emails

## Support

- **MCP Protocol:** https://modelcontextprotocol.io/
- **Gmail API:** https://developers.google.com/gmail/api
- **OAuth2 Issues:** https://developers.google.com/identity/protocols/oauth2

## Success!

If you've completed all steps, you now have a fully functional Gmail MCP Server!

Try saying to Claude:
> "Show me my 5 most recent unread emails"

Enjoy your AI-powered email assistant! 🎉
