#!/usr/bin/env node

/**
 * Gmail MCP Server
 *
 * A production-ready Model Context Protocol server for Gmail integration.
 * Provides tools for sending emails, drafting emails, and searching messages.
 *
 * @requires @modelcontextprotocol/sdk
 * @requires googleapis
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Constants
const CONFIG_PATH = path.join(__dirname, "config.json");
const TOKEN_PATH = path.join(__dirname, "token.json");

/**
 * Logger that writes to stderr to avoid corrupting stdio transport
 */
const logger = {
  info: (msg, ...args) => console.error(`[INFO] ${msg}`, ...args),
  error: (msg, ...args) => console.error(`[ERROR] ${msg}`, ...args),
  warn: (msg, ...args) => console.error(`[WARN] ${msg}`, ...args),
  debug: (msg, ...args) => console.error(`[DEBUG] ${msg}`, ...args),
};

/**
 * Load OAuth2 credentials from config.json
 */
async function loadCredentials() {
  try {
    const configData = await fs.readFile(CONFIG_PATH, "utf8");
    const config = JSON.parse(configData);

    if (!config.installed && !config.web) {
      throw new Error("Invalid config.json format. Expected 'installed' or 'web' credentials.");
    }

    return config.installed || config.web;
  } catch (error) {
    logger.error("Failed to load credentials:", error.message);
    throw new Error(`Could not load config.json from ${CONFIG_PATH}. Please ensure it exists and is valid.`);
  }
}

/**
 * Load OAuth2 token from token.json
 */
async function loadToken() {
  try {
    const tokenData = await fs.readFile(TOKEN_PATH, "utf8");
    return JSON.parse(tokenData);
  } catch (error) {
    throw new Error(`Could not load token.json from ${TOKEN_PATH}. Please run OAuth flow first.`);
  }
}

/**
 * Initialize Gmail API client with OAuth2
 */
async function initializeGmailClient() {
  const credentials = await loadCredentials();
  const token = await loadToken();

  const { client_id, client_secret, redirect_uris } = credentials;
  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0]
  );

  oauth2Client.setCredentials(token);

  return google.gmail({ version: "v1", auth: oauth2Client });
}

/**
 * Send an email via Gmail API
 */
async function sendEmail(gmail, to, subject, body, attachments = []) {
  try {
    // Create email message
    const boundary = "foo_bar_baz";
    let message = [
      `To: ${to}`,
      `Subject: ${subject}`,
      "MIME-Version: 1.0",
      `Content-Type: multipart/mixed; boundary="${boundary}"`,
      "",
      `--${boundary}`,
      "Content-Type: text/html; charset=utf-8",
      "",
      body,
    ];

    // Add attachments if provided
    for (const attachment of attachments) {
      const { filename, content, mimeType } = attachment;
      message.push(
        `--${boundary}`,
        `Content-Type: ${mimeType}`,
        `Content-Disposition: attachment; filename="${filename}"`,
        "Content-Transfer-Encoding: base64",
        "",
        content,
      );
    }

    message.push(`--${boundary}--`);

    const encodedMessage = Buffer.from(message.join("\n"))
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    const response = await gmail.users.messages.send({
      userId: "me",
      requestBody: {
        raw: encodedMessage,
      },
    });

    logger.info(`Email sent successfully. Message ID: ${response.data.id}`);
    return {
      success: true,
      messageId: response.data.id,
      threadId: response.data.threadId,
    };
  } catch (error) {
    logger.error("Failed to send email:", error.message);
    throw new Error(`Failed to send email: ${error.message}`);
  }
}

/**
 * Create a draft email in Gmail
 */
async function draftEmail(gmail, to, subject, body) {
  try {
    const message = [
      `To: ${to}`,
      `Subject: ${subject}`,
      "MIME-Version: 1.0",
      "Content-Type: text/html; charset=utf-8",
      "",
      body,
    ].join("\n");

    const encodedMessage = Buffer.from(message)
      .toString("base64")
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

    const response = await gmail.users.drafts.create({
      userId: "me",
      requestBody: {
        message: {
          raw: encodedMessage,
        },
      },
    });

    logger.info(`Draft created successfully. Draft ID: ${response.data.id}`);
    return {
      success: true,
      draftId: response.data.id,
      messageId: response.data.message.id,
    };
  } catch (error) {
    logger.error("Failed to create draft:", error.message);
    throw new Error(`Failed to create draft: ${error.message}`);
  }
}

/**
 * Search emails in Gmail
 */
async function searchEmails(gmail, query, maxResults = 10) {
  try {
    // Search for messages matching the query
    const listResponse = await gmail.users.messages.list({
      userId: "me",
      q: query,
      maxResults: maxResults,
    });

    if (!listResponse.data.messages || listResponse.data.messages.length === 0) {
      return {
        success: true,
        count: 0,
        messages: [],
      };
    }

    // Fetch full message details
    const messages = await Promise.all(
      listResponse.data.messages.map(async (message) => {
        const details = await gmail.users.messages.get({
          userId: "me",
          id: message.id,
          format: "full",
        });

        const headers = details.data.payload.headers;
        const subject = headers.find((h) => h.name === "Subject")?.value || "(No Subject)";
        const from = headers.find((h) => h.name === "From")?.value || "(Unknown)";
        const date = headers.find((h) => h.name === "Date")?.value || "(No Date)";
        const to = headers.find((h) => h.name === "To")?.value || "(Unknown)";

        // Extract body
        let body = "";
        if (details.data.payload.body?.data) {
          body = Buffer.from(details.data.payload.body.data, "base64").toString("utf-8");
        } else if (details.data.payload.parts) {
          const textPart = details.data.payload.parts.find(
            (part) => part.mimeType === "text/plain" || part.mimeType === "text/html"
          );
          if (textPart?.body?.data) {
            body = Buffer.from(textPart.body.data, "base64").toString("utf-8");
          }
        }

        return {
          id: message.id,
          threadId: message.threadId,
          subject,
          from,
          to,
          date,
          snippet: details.data.snippet,
          body: body.substring(0, 500), // Limit body preview
        };
      })
    );

    logger.info(`Found ${messages.length} messages matching query: ${query}`);
    return {
      success: true,
      count: messages.length,
      resultSizeEstimate: listResponse.data.resultSizeEstimate,
      messages,
    };
  } catch (error) {
    logger.error("Failed to search emails:", error.message);
    throw new Error(`Failed to search emails: ${error.message}`);
  }
}

/**
 * Main server implementation
 */
async function main() {
  logger.info("Starting Gmail MCP Server...");

  let gmail;
  try {
    gmail = await initializeGmailClient();
    logger.info("Gmail API client initialized successfully");
  } catch (error) {
    logger.error("Failed to initialize Gmail client:", error.message);
    process.exit(1);
  }

  // Create MCP server instance
  const server = new Server(
    {
      name: "gmail-mcp-server",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register tool handlers
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: "send_email",
          description: "Send an email via Gmail. Requires recipient email, subject, and body. Optionally supports attachments (base64 encoded).",
          inputSchema: {
            type: "object",
            properties: {
              to: {
                type: "string",
                description: "Recipient email address (e.g., user@example.com)",
              },
              subject: {
                type: "string",
                description: "Email subject line",
              },
              body: {
                type: "string",
                description: "Email body content (supports HTML)",
              },
              attachments: {
                type: "array",
                description: "Optional array of attachments",
                items: {
                  type: "object",
                  properties: {
                    filename: { type: "string" },
                    content: { type: "string", description: "Base64 encoded content" },
                    mimeType: { type: "string", description: "MIME type (e.g., 'application/pdf')" },
                  },
                  required: ["filename", "content", "mimeType"],
                },
              },
            },
            required: ["to", "subject", "body"],
          },
        },
        {
          name: "draft_email",
          description: "Create a draft email in Gmail. The draft can be edited and sent later through Gmail UI.",
          inputSchema: {
            type: "object",
            properties: {
              to: {
                type: "string",
                description: "Recipient email address",
              },
              subject: {
                type: "string",
                description: "Email subject line",
              },
              body: {
                type: "string",
                description: "Email body content (supports HTML)",
              },
            },
            required: ["to", "subject", "body"],
          },
        },
        {
          name: "search_emails",
          description: "Search emails in Gmail using Gmail's search syntax. Supports queries like 'from:user@example.com', 'subject:meeting', 'is:unread', etc.",
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "Gmail search query (e.g., 'from:user@example.com subject:invoice')",
              },
              max_results: {
                type: "number",
                description: "Maximum number of results to return (default: 10, max: 100)",
                default: 10,
              },
            },
            required: ["query"],
          },
        },
      ],
    };
  });

  // Handle tool execution
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case "send_email": {
          const { to, subject, body, attachments = [] } = args;

          if (!to || !subject || !body) {
            return {
              content: [
                {
                  type: "text",
                  text: "Error: Missing required parameters. 'to', 'subject', and 'body' are required.",
                },
              ],
            };
          }

          const result = await sendEmail(gmail, to, subject, body, attachments);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case "draft_email": {
          const { to, subject, body } = args;

          if (!to || !subject || !body) {
            return {
              content: [
                {
                  type: "text",
                  text: "Error: Missing required parameters. 'to', 'subject', and 'body' are required.",
                },
              ],
            };
          }

          const result = await draftEmail(gmail, to, subject, body);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        case "search_emails": {
          const { query, max_results = 10 } = args;

          if (!query) {
            return {
              content: [
                {
                  type: "text",
                  text: "Error: Missing required parameter 'query'.",
                },
              ],
            };
          }

          const maxResultsNum = Math.min(Math.max(1, max_results), 100);
          const result = await searchEmails(gmail, query, maxResultsNum);
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2),
              },
            ],
          };
        }

        default:
          return {
            content: [
              {
                type: "text",
                text: `Error: Unknown tool '${name}'`,
              },
            ],
            isError: true,
          };
      }
    } catch (error) {
      logger.error(`Error executing tool '${name}':`, error.message);
      return {
        content: [
          {
            type: "text",
            text: `Error: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  });

  // Connect to stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  logger.info("Gmail MCP Server is running on stdio");
}

// Handle graceful shutdown
process.on("SIGINT", () => {
  logger.info("Shutting down Gmail MCP Server...");
  process.exit(0);
});

process.on("SIGTERM", () => {
  logger.info("Shutting down Gmail MCP Server...");
  process.exit(0);
});

// Start the server
main().catch((error) => {
  logger.error("Fatal error:", error);
  process.exit(1);
});
