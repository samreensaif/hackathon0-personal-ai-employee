# Gmail MCP Server

A production-ready Model Context Protocol (MCP) server for Gmail integration. This server enables AI assistants to send emails, create drafts, and search through Gmail messages using OAuth2 authentication.

## Features

- **Send Email**: Send emails with optional attachments
- **Draft Email**: Create draft emails for later review and sending
- **Search Emails**: Search through Gmail using Gmail's powerful query syntax
- **OAuth2 Authentication**: Secure authentication using Google's OAuth2
- **Error Handling**: Comprehensive error handling and logging
- **Production Ready**: Follows MCP best practices with proper stdio transport

## Prerequisites

- Node.js 16 or higher
- A Google Cloud Project with Gmail API enabled
- Gmail account

## Installation

1. Install dependencies:

```bash
npm install @modelcontextprotocol/sdk googleapis
```

2. Make the server executable:

```bash
chmod +x server.js
```

## Setup Instructions

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Step 2: Enable Gmail API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click "Enable"

### Step 3: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure the OAuth consent screen if prompted:
   - User Type: Choose "External" for testing
   - Add your email as a test user
   - Scopes: Add the Gmail API scopes (they'll be requested during authorization)
4. Application type: Select "Desktop app" or "Web application"
5. Name: Give it a descriptive name (e.g., "Gmail MCP Server")
6. Click "Create"
7. Download the JSON file

### Step 4: Configure the Server

1. Rename the downloaded JSON file to `config.json`
2. Move it to the `mcp_servers/email/` directory
3. Verify the format matches this structure:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

### Step 5: Run OAuth Authorization Flow

Create a helper script to obtain the OAuth token:

```javascript
// auth.js
import { google } from 'googleapis';
import { promises as fs } from 'fs';
import readline from 'readline';

const SCOPES = [
  'https://www.googleapis.com/auth/gmail.send',
  'https://www.googleapis.com/auth/gmail.compose',
  'https://www.googleapis.com/auth/gmail.readonly',
  'https://www.googleapis.com/auth/gmail.modify'
];

async function authorize() {
  const content = await fs.readFile('config.json', 'utf8');
  const credentials = JSON.parse(content);
  const { client_id, client_secret, redirect_uris } = credentials.installed;

  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0]
  );

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });

  console.log('Authorize this app by visiting this url:', authUrl);

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question('Enter the code from that page here: ', async (code) => {
      rl.close();
      const { tokens } = await oauth2Client.getToken(code);
      await fs.writeFile('token.json', JSON.stringify(tokens, null, 2));
      console.log('Token stored to token.json');
      resolve();
    });
  });
}

authorize().catch(console.error);
```

Run the authorization:

```bash
node auth.js
```

Follow the URL, authorize the application, and paste the code back. This creates `token.json`.

### Step 6: Configure Claude for Desktop

Add the server to your Claude for Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

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

Replace `/ABSOLUTE/PATH/TO/` with the actual path to your server.

### Step 7: Restart Claude for Desktop

Completely quit and restart Claude for Desktop (Cmd+Q on macOS, not just closing the window).

## Required OAuth2 Scopes

The server requires these Gmail API scopes:

- `https://www.googleapis.com/auth/gmail.send` - Send emails
- `https://www.googleapis.com/auth/gmail.compose` - Create and manage drafts
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails and search
- `https://www.googleapis.com/auth/gmail.modify` - Modify emails (for draft operations)

## Available Tools

### 1. send_email

Send an email via Gmail with optional attachments.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body (supports HTML)
- `attachments` (array, optional): Array of attachment objects
  - `filename` (string): Name of the file
  - `content` (string): Base64 encoded file content
  - `mimeType` (string): MIME type (e.g., 'application/pdf')

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Meeting Follow-up",
  "body": "<p>Hi there,</p><p>Following up on our meeting...</p>",
  "attachments": [
    {
      "filename": "report.pdf",
      "content": "JVBERi0xLjQKJeLjz9MK...",
      "mimeType": "application/pdf"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "messageId": "18d4f2c5a9b2e8f1",
  "threadId": "18d4f2c5a9b2e8f1"
}
```

### 2. draft_email

Create a draft email in Gmail.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body (supports HTML)

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Draft: Project Update",
  "body": "<p>Draft email content...</p>"
}
```

**Response:**
```json
{
  "success": true,
  "draftId": "r-7234567890123456789",
  "messageId": "18d4f2c5a9b2e8f1"
}
```

### 3. search_emails

Search emails using Gmail's search syntax.

**Parameters:**
- `query` (string, required): Gmail search query
- `max_results` (number, optional): Maximum results to return (default: 10, max: 100)

**Search Query Examples:**
- `from:user@example.com` - Emails from specific sender
- `subject:invoice` - Emails with "invoice" in subject
- `is:unread` - Unread emails
- `has:attachment` - Emails with attachments
- `after:2024/01/01` - Emails after a date
- `from:user@example.com subject:meeting` - Combined criteria

**Example:**
```json
{
  "query": "from:boss@company.com is:unread",
  "max_results": 5
}
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "resultSizeEstimate": 2,
  "messages": [
    {
      "id": "18d4f2c5a9b2e8f1",
      "threadId": "18d4f2c5a9b2e8f1",
      "subject": "Project Update Required",
      "from": "boss@company.com",
      "to": "you@company.com",
      "date": "Wed, 5 Feb 2026 10:30:00 -0800",
      "snippet": "Please provide an update on the project...",
      "body": "Hi,\n\nPlease provide an update on the project status by EOD..."
    }
  ]
}
```

## Usage Examples in Claude

Once configured, you can use natural language commands:

1. **Sending emails:**
   - "Send an email to john@example.com with subject 'Meeting Tomorrow' and body 'Let's meet at 2pm'"
   - "Email the report to my manager at manager@company.com"

2. **Creating drafts:**
   - "Draft an email to client@company.com about the project delay"
   - "Create a draft email for the weekly team update"

3. **Searching emails:**
   - "Find all unread emails from my boss"
   - "Search for emails about invoices from last week"
   - "Show me emails with attachments from john@example.com"

## Security Best Practices

1. **Never commit credentials**: Add `config.json` and `token.json` to `.gitignore`
2. **Limit scopes**: Only request the Gmail scopes you need
3. **Token refresh**: The OAuth2 client automatically refreshes expired tokens
4. **Secure storage**: Store `token.json` with restricted permissions (chmod 600)
5. **OAuth consent screen**: Configure your OAuth consent screen properly for production use
6. **Rate limiting**: Gmail API has rate limits; the server handles errors gracefully

## Troubleshooting

### Server not appearing in Claude for Desktop

1. Check Claude's logs:
   - macOS: `~/Library/Logs/Claude/mcp.log`
   - Windows: `%APPDATA%\Claude\logs\mcp.log`
2. Verify absolute paths in configuration
3. Ensure Node.js is in your PATH
4. Completely restart Claude for Desktop (Cmd+Q, not just close window)

### Authentication Errors

1. Verify `config.json` format matches the expected structure
2. Re-run the OAuth flow (`node auth.js`) if token is expired
3. Check that all required scopes are included
4. Ensure Gmail API is enabled in Google Cloud Console

### Tool Execution Failures

1. Check server logs (written to stderr)
2. Verify Gmail API quotas haven't been exceeded
3. Ensure the token has proper scopes
4. Check network connectivity

### Invalid Token Error

If you see "invalid_grant" errors:
1. Delete `token.json`
2. Re-run the OAuth flow: `node auth.js`
3. Ensure you're authorizing with the correct Google account

## File Structure

```
mcp_servers/email/
├── server.js          # Main MCP server implementation
├── config.json        # OAuth2 credentials (DO NOT COMMIT)
├── token.json         # OAuth2 token (DO NOT COMMIT, auto-generated)
├── auth.js            # Helper script for OAuth flow
├── package.json       # Node.js dependencies
└── README.md          # This file
```

## Development and Testing

### Testing the Server Standalone

You can test the server using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector node server.js
```

### Logging

All logs are written to stderr to avoid corrupting the stdio transport. Check logs for debugging:

```bash
node server.js 2> gmail-server.log
```

## API Rate Limits

Gmail API has the following default quotas:
- 1 billion quota units per day
- Sending emails: 100-500 per day (depends on account type)
- Search queries: 250 quota units per user per second

The server handles rate limit errors gracefully and returns informative error messages.

## Production Deployment

For production use:

1. Configure OAuth consent screen for production (not testing)
2. Implement token refresh handling (already included)
3. Monitor API quotas in Google Cloud Console
4. Set up proper error monitoring and alerting
5. Consider using a service account for organization-wide deployments

## License

This MCP server is provided as-is for use with the Model Context Protocol.

## Support

For issues related to:
- **MCP Protocol**: See [MCP Documentation](https://modelcontextprotocol.io/)
- **Gmail API**: See [Gmail API Documentation](https://developers.google.com/gmail/api)
- **OAuth2**: See [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)

## Changelog

### Version 1.0.0
- Initial release
- Support for sending emails, creating drafts, and searching
- OAuth2 authentication
- Comprehensive error handling
- Production-ready implementation
