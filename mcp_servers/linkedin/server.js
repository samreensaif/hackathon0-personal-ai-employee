#!/usr/bin/env node

/**
 * LinkedIn MCP Server (File-Based Draft System)
 *
 * IMPORTANT: LinkedIn's official API requires company approval.
 *
 * OPTION A (IMPLEMENTED): File-Based Integration - RECOMMENDED FOR HACKATHON
 * ========================================================================
 * - MCP creates draft posts in LinkedIn_Drafts/ folder
 * - Human manually posts to LinkedIn
 * - MCP logs the "draft created" action
 * - Safe (no risk of account suspension)
 * - Compliant (no API violations)
 * - Audit-friendly (all drafts are tracked)
 * - Demo-ready (perfect for hackathons/prototypes)
 *
 * OPTION B (NOT IMPLEMENTED): Unofficial API - USE WITH EXTREME CAUTION
 * =====================================================================
 * - Would use puppeteer/playwright to automate LinkedIn web interface
 * - Requires LinkedIn session cookies (expires frequently)
 * - HIGH RISK of account suspension
 * - VIOLATES LinkedIn Terms of Service
 * - Only for authorized testing/research in controlled environments
 * - See implementation notes at bottom of file
 *
 * For production automation, apply for LinkedIn Marketing Developer Platform:
 * https://www.linkedin.com/developers/
 *
 * @requires @modelcontextprotocol/sdk
 * @version 1.0.0
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import crypto from "crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const VAULT_PATH = path.join(PROJECT_ROOT, "AI_Employee_Vault");
const DRAFTS_PATH = path.join(VAULT_PATH, "LinkedIn_Drafts");
const LOGS_PATH = path.join(VAULT_PATH, "Logs");
const RATE_LIMIT_FILE = path.join(LOGS_PATH, "linkedin_rate_limits.json");

// Configuration
const CONFIG = {
  // Rate limiting
  maxPostsPerHour: 1,
  maxPostsPerDay: 3,
  maxDraftsPerDay: 20,

  // Content limits (LinkedIn specifications)
  maxContentLength: 3000,
  maxHashtags: 30,
  recommendedHashtags: 5,

  // Best posting times (UTC)
  bestPostingTimes: [
    { day: "weekday", hours: [8, 9, 12, 17, 18] },
    { day: "weekend", hours: [10, 11, 15] }
  ],

  // Content guidelines
  urlPattern: /https?:\/\/[^\s]+/g,
  hashtagPattern: /#[\w]+/g,
  mentionPattern: /@[\w]+/g
};

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
 * Ensure required directories exist
 */
async function ensureDirectories() {
  const dirs = [VAULT_PATH, DRAFTS_PATH, LOGS_PATH];

  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true });
      logger.debug(`Ensured directory exists: ${dir}`);
    } catch (error) {
      logger.error(`Failed to create directory ${dir}:`, error.message);
      throw error;
    }
  }
}

/**
 * Generate unique draft ID
 */
function generateDraftId() {
  return `li_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
}

/**
 * Load rate limit data
 */
async function loadRateLimits() {
  try {
    const data = await fs.readFile(RATE_LIMIT_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return {
      posts: [],
      drafts: []
    };
  }
}

/**
 * Save rate limit data
 */
async function saveRateLimits(data) {
  await fs.writeFile(RATE_LIMIT_FILE, JSON.stringify(data, null, 2));
}

/**
 * Check if rate limits allow action
 */
async function checkRateLimit(action = 'draft') {
  const limits = await loadRateLimits();
  const now = new Date();
  const oneHourAgo = new Date(now - 60 * 60 * 1000);
  const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);

  const actionList = action === 'post' ? limits.posts : limits.drafts;

  // Clean old entries
  const recentActions = actionList.filter(timestamp =>
    new Date(timestamp) > oneDayAgo
  );

  // Count recent actions
  const lastHour = recentActions.filter(timestamp =>
    new Date(timestamp) > oneHourAgo
  ).length;

  const lastDay = recentActions.length;

  // Check limits
  const maxHour = action === 'post' ? CONFIG.maxPostsPerHour : CONFIG.maxPostsPerHour;
  const maxDay = action === 'post' ? CONFIG.maxPostsPerDay : CONFIG.maxDraftsPerDay;

  if (lastHour >= maxHour) {
    return {
      allowed: false,
      reason: `Rate limit exceeded: ${lastHour}/${maxHour} ${action}s in the last hour`,
      resetTime: new Date(Math.min(...actionList.map(t => new Date(t))) + 60 * 60 * 1000)
    };
  }

  if (lastDay >= maxDay) {
    return {
      allowed: false,
      reason: `Rate limit exceeded: ${lastDay}/${maxDay} ${action}s in the last day`,
      resetTime: new Date(Math.min(...actionList.map(t => new Date(t))) + 24 * 60 * 60 * 1000)
    };
  }

  return {
    allowed: true,
    remaining: {
      hour: maxHour - lastHour,
      day: maxDay - lastDay
    }
  };
}

/**
 * Record action for rate limiting
 */
async function recordAction(action = 'draft') {
  const limits = await loadRateLimits();
  const now = new Date().toISOString();

  if (action === 'post') {
    limits.posts.push(now);
  } else {
    limits.drafts.push(now);
  }

  await saveRateLimits(limits);
}

/**
 * Validate post content
 */
function validateContent(content) {
  const errors = [];
  const warnings = [];

  // Check length
  if (!content || content.trim().length === 0) {
    errors.push("Content cannot be empty");
  }

  if (content.length > CONFIG.maxContentLength) {
    errors.push(`Content exceeds maximum length: ${content.length}/${CONFIG.maxContentLength} characters`);
  }

  // Count hashtags
  const hashtags = content.match(CONFIG.hashtagPattern) || [];
  if (hashtags.length > CONFIG.maxHashtags) {
    warnings.push(`Too many hashtags (${hashtags.length}). LinkedIn recommends ${CONFIG.recommendedHashtags} or fewer.`);
  }

  // Check for URLs
  const urls = content.match(CONFIG.urlPattern) || [];
  if (urls.length > 3) {
    warnings.push(`Multiple URLs detected (${urls.length}). Consider limiting to 1-2 for better engagement.`);
  }

  // Check for length sweet spot
  if (content.length < 150) {
    warnings.push("Content is quite short. LinkedIn posts with 150-300 characters tend to perform better.");
  } else if (content.length > 1500) {
    warnings.push("Long post detected. Consider breaking into multiple posts or using LinkedIn articles.");
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    stats: {
      length: content.length,
      hashtags: hashtags.length,
      urls: urls.length,
      mentions: (content.match(CONFIG.mentionPattern) || []).length
    }
  };
}

/**
 * Suggest relevant hashtags based on content
 */
function suggestHashtags(content) {
  // Common professional hashtags by category
  const categories = {
    business: ['#Business', '#Entrepreneurship', '#Leadership', '#Strategy', '#Innovation'],
    technology: ['#Technology', '#TechNews', '#AI', '#MachineLearning', '#SoftwareDevelopment'],
    marketing: ['#Marketing', '#DigitalMarketing', '#ContentMarketing', '#SocialMedia', '#Branding'],
    career: ['#Career', '#JobSearch', '#Hiring', '#CareerAdvice', '#ProfessionalDevelopment'],
    productivity: ['#Productivity', '#TimeManagement', '#WorkLifeBalance', '#RemoteWork', '#Efficiency'],
    finance: ['#Finance', '#Investing', '#FinTech', '#Economics', '#Business'],
    sales: ['#Sales', '#B2B', '#SaaS', '#CustomerSuccess', '#SalesStrategy']
  };

  const suggestions = [];
  const contentLower = content.toLowerCase();

  // Match keywords to categories
  for (const [category, tags] of Object.entries(categories)) {
    const keywords = {
      business: ['business', 'company', 'startup', 'entrepreneur', 'ceo'],
      technology: ['tech', 'software', 'ai', 'data', 'code', 'development'],
      marketing: ['marketing', 'brand', 'content', 'social media', 'campaign'],
      career: ['career', 'job', 'hiring', 'interview', 'resume'],
      productivity: ['productivity', 'time', 'work', 'efficiency', 'remote'],
      finance: ['finance', 'money', 'investment', 'revenue', 'profit'],
      sales: ['sales', 'customer', 'client', 'deal', 'revenue']
    };

    const categoryKeywords = keywords[category] || [];
    if (categoryKeywords.some(kw => contentLower.includes(kw))) {
      suggestions.push(...tags.slice(0, 2));
    }
  }

  // Return top 5 unique suggestions
  return [...new Set(suggestions)].slice(0, CONFIG.recommendedHashtags);
}

/**
 * Get best posting time recommendations
 */
function getBestPostingTimes() {
  const now = new Date();
  const day = now.getDay(); // 0 = Sunday, 6 = Saturday
  const isWeekend = day === 0 || day === 6;

  const times = isWeekend
    ? CONFIG.bestPostingTimes.find(t => t.day === 'weekend')
    : CONFIG.bestPostingTimes.find(t => t.day === 'weekday');

  const recommendations = times.hours.map(hour => {
    const recommendedTime = new Date(now);
    recommendedTime.setHours(hour, 0, 0, 0);

    // If time has passed today, suggest tomorrow
    if (recommendedTime < now) {
      recommendedTime.setDate(recommendedTime.getDate() + 1);
    }

    return {
      time: recommendedTime.toISOString(),
      localTime: recommendedTime.toLocaleString(),
      hoursFromNow: Math.round((recommendedTime - now) / (1000 * 60 * 60))
    };
  });

  return {
    recommendations,
    tip: isWeekend
      ? "Weekend posts get less engagement. Consider scheduling for Monday morning."
      : "Best engagement on weekdays during business hours (8-9 AM, 12 PM, 5-6 PM)."
  };
}

/**
 * Create draft post
 */
async function createDraft(content, metadata = {}) {
  // Validate content
  const validation = validateContent(content);
  if (!validation.valid) {
    throw new Error(`Invalid content: ${validation.errors.join(', ')}`);
  }

  // Check rate limits
  const rateCheck = await checkRateLimit('draft');
  if (!rateCheck.allowed) {
    throw new Error(rateCheck.reason);
  }

  // Generate draft ID
  const draftId = generateDraftId();
  const timestamp = new Date().toISOString();

  // Get suggestions
  const hashtags = suggestHashtags(content);
  const bestTimes = getBestPostingTimes();

  // Create draft object
  const draft = {
    draftId,
    createdAt: timestamp,
    status: 'draft',
    content,
    metadata: {
      ...metadata,
      validation,
      suggestedHashtags: hashtags,
      bestPostingTimes: bestTimes
    },
    posting: {
      method: 'manual',
      instructions: [
        '1. Open LinkedIn in your browser',
        '2. Click "Start a post"',
        '3. Copy the content from this draft',
        '4. Add any images or media',
        '5. Review and post',
        '6. Update draft status to "posted" when done'
      ]
    }
  };

  // Save draft file
  const filename = `${draftId}.json`;
  const filepath = path.join(DRAFTS_PATH, filename);
  await fs.writeFile(filepath, JSON.stringify(draft, null, 2));

  // Create human-readable version
  const readableFilename = `${draftId}.md`;
  const readablePath = path.join(DRAFTS_PATH, readableFilename);
  const readableContent = formatDraftAsMarkdown(draft);
  await fs.writeFile(readablePath, readableContent);

  // Record action
  await recordAction('draft');

  // Log to daily log
  await logAction('draft_created', {
    draftId,
    contentLength: content.length,
    hashtags: validation.stats.hashtags,
    warnings: validation.warnings
  });

  logger.info(`Draft created: ${draftId}`);

  return {
    success: true,
    draftId,
    filepath,
    readablePath,
    validation,
    suggestedHashtags: hashtags,
    bestPostingTimes: bestTimes,
    rateLimit: rateCheck.remaining
  };
}

/**
 * Format draft as readable markdown
 */
function formatDraftAsMarkdown(draft) {
  const { content, metadata, posting, draftId, createdAt } = draft;

  let md = `# LinkedIn Post Draft\n\n`;
  md += `**Draft ID:** ${draftId}\n`;
  md += `**Created:** ${new Date(createdAt).toLocaleString()}\n`;
  md += `**Status:** ${draft.status}\n\n`;

  md += `---\n\n`;
  md += `## Content\n\n`;
  md += `${content}\n\n`;

  if (metadata.suggestedHashtags && metadata.suggestedHashtags.length > 0) {
    md += `---\n\n`;
    md += `## Suggested Hashtags\n\n`;
    md += metadata.suggestedHashtags.join(' ') + '\n\n';
  }

  if (metadata.validation.warnings.length > 0) {
    md += `---\n\n`;
    md += `## Content Warnings\n\n`;
    metadata.validation.warnings.forEach(w => {
      md += `- ⚠️  ${w}\n`;
    });
    md += `\n`;
  }

  md += `---\n\n`;
  md += `## Content Stats\n\n`;
  md += `- Length: ${metadata.validation.stats.length} characters\n`;
  md += `- Hashtags: ${metadata.validation.stats.hashtags}\n`;
  md += `- URLs: ${metadata.validation.stats.urls}\n`;
  md += `- Mentions: ${metadata.validation.stats.mentions}\n\n`;

  if (metadata.bestPostingTimes) {
    md += `---\n\n`;
    md += `## Best Posting Times\n\n`;
    md += `${metadata.bestPostingTimes.tip}\n\n`;
    metadata.bestPostingTimes.recommendations.slice(0, 3).forEach((rec, i) => {
      md += `${i + 1}. ${rec.localTime} (${rec.hoursFromNow}h from now)\n`;
    });
    md += `\n`;
  }

  md += `---\n\n`;
  md += `## How to Post\n\n`;
  posting.instructions.forEach((instruction, i) => {
    md += `${instruction}\n`;
  });
  md += `\n`;

  md += `---\n\n`;
  md += `## After Posting\n\n`;
  md += `Update this draft's status by editing \`${draftId}.json\`:\n\n`;
  md += `\`\`\`json\n`;
  md += `{\n`;
  md += `  "status": "posted",\n`;
  md += `  "postedAt": "${new Date().toISOString()}",\n`;
  md += `  "postUrl": "https://linkedin.com/posts/your-post-url"\n`;
  md += `}\n`;
  md += `\`\`\`\n\n`;

  return md;
}

/**
 * Get draft status
 */
async function getDraftStatus(draftId) {
  const filepath = path.join(DRAFTS_PATH, `${draftId}.json`);

  try {
    const data = await fs.readFile(filepath, 'utf8');
    const draft = JSON.parse(data);

    return {
      success: true,
      draft,
      filepath
    };
  } catch (error) {
    throw new Error(`Draft not found: ${draftId}`);
  }
}

/**
 * List all drafts
 */
async function listDrafts(status = null) {
  try {
    const files = await fs.readdir(DRAFTS_PATH);
    const jsonFiles = files.filter(f => f.endsWith('.json'));

    const drafts = await Promise.all(
      jsonFiles.map(async (file) => {
        const filepath = path.join(DRAFTS_PATH, file);
        const data = await fs.readFile(filepath, 'utf8');
        return JSON.parse(data);
      })
    );

    // Filter by status if provided
    const filtered = status
      ? drafts.filter(d => d.status === status)
      : drafts;

    // Sort by creation date (newest first)
    filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    return {
      success: true,
      count: filtered.length,
      drafts: filtered
    };
  } catch (error) {
    return {
      success: true,
      count: 0,
      drafts: []
    };
  }
}

/**
 * Log action to daily log file
 */
async function logAction(action, details) {
  const today = new Date().toISOString().split('T')[0];
  const logFile = path.join(LOGS_PATH, `${today}.json`);

  const logEntry = {
    timestamp: new Date().toISOString(),
    source: 'linkedin_mcp',
    action,
    ...details
  };

  try {
    let logs = [];
    try {
      const data = await fs.readFile(logFile, 'utf8');
      logs = JSON.parse(data);
    } catch {
      logs = [];
    }

    logs.push(logEntry);
    await fs.writeFile(logFile, JSON.stringify(logs, null, 2));
  } catch (error) {
    logger.error('Failed to write log:', error.message);
  }
}

/**
 * Main server setup
 */
async function main() {
  logger.info("Starting LinkedIn MCP Server (File-Based)");

  // Ensure directories exist
  await ensureDirectories();

  const server = new Server(
    {
      name: "linkedin-server",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: "create_linkedin_post",
          description: "Create a LinkedIn post draft with content validation and best practice suggestions. Draft is saved for manual posting.",
          inputSchema: {
            type: "object",
            properties: {
              content: {
                type: "string",
                description: "The post content (max 3000 characters)"
              },
              schedule_time: {
                type: "string",
                description: "Optional: Suggested posting time (ISO 8601 format)"
              },
              tags: {
                type: "array",
                items: { type: "string" },
                description: "Optional: Custom tags for organizing drafts"
              }
            },
            required: ["content"]
          }
        },
        {
          name: "save_linkedin_draft",
          description: "Save a LinkedIn post draft without immediate posting intent. Same as create_linkedin_post but semantic difference.",
          inputSchema: {
            type: "object",
            properties: {
              content: {
                type: "string",
                description: "The draft content"
              },
              notes: {
                type: "string",
                description: "Optional: Notes about this draft"
              }
            },
            required: ["content"]
          }
        },
        {
          name: "get_draft_status",
          description: "Get the status and details of a LinkedIn post draft by ID",
          inputSchema: {
            type: "object",
            properties: {
              draft_id: {
                type: "string",
                description: "The draft ID to look up"
              }
            },
            required: ["draft_id"]
          }
        },
        {
          name: "list_linkedin_drafts",
          description: "List all LinkedIn post drafts, optionally filtered by status",
          inputSchema: {
            type: "object",
            properties: {
              status: {
                type: "string",
                enum: ["draft", "posted", "archived"],
                description: "Optional: Filter by status"
              }
            }
          }
        },
        {
          name: "validate_linkedin_content",
          description: "Validate LinkedIn post content and get suggestions without creating a draft",
          inputSchema: {
            type: "object",
            properties: {
              content: {
                type: "string",
                description: "Content to validate"
              }
            },
            required: ["content"]
          }
        },
        {
          name: "get_posting_recommendations",
          description: "Get best posting time recommendations and engagement tips",
          inputSchema: {
            type: "object",
            properties: {}
          }
        }
      ]
    };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
      const { name, arguments: args } = request.params;

      switch (name) {
        case "create_linkedin_post": {
          const result = await createDraft(args.content, {
            scheduleTime: args.schedule_time,
            tags: args.tags || []
          });

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2)
              }
            ]
          };
        }

        case "save_linkedin_draft": {
          const result = await createDraft(args.content, {
            notes: args.notes,
            type: 'draft'
          });

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2)
              }
            ]
          };
        }

        case "get_draft_status": {
          const result = await getDraftStatus(args.draft_id);

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2)
              }
            ]
          };
        }

        case "list_linkedin_drafts": {
          const result = await listDrafts(args.status);

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2)
              }
            ]
          };
        }

        case "validate_linkedin_content": {
          const validation = validateContent(args.content);
          const hashtags = suggestHashtags(args.content);

          const result = {
            validation,
            suggestedHashtags: hashtags,
            recommendations: validation.warnings.length === 0
              ? ["Content looks good! Ready to post."]
              : validation.warnings
          };

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2)
              }
            ]
          };
        }

        case "get_posting_recommendations": {
          const recommendations = getBestPostingTimes();
          const rateCheck = await checkRateLimit('post');

          const result = {
            ...recommendations,
            rateLimit: rateCheck
          };

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(result, null, 2)
              }
            ]
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      logger.error("Tool execution error:", error);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: false,
              error: error.message
            })
          }
        ],
        isError: true,
      };
    }
  });

  // Start server
  const transport = new StdioServerTransport();
  await server.connect(transport);

  logger.info("LinkedIn MCP Server running");
}

// Run server
main().catch((error) => {
  logger.error("Fatal error:", error);
  process.exit(1);
});

/**
 * ==============================================================================
 * OPTION B: UNOFFICIAL API IMPLEMENTATION (NOT IMPLEMENTED - EDUCATIONAL ONLY)
 * ==============================================================================
 *
 * ⚠️  WARNING: UNAUTHORIZED USE MAY RESULT IN PERMANENT ACCOUNT BAN ⚠️
 *
 * LinkedIn's Terms of Service explicitly prohibit automated posting through
 * unofficial means. This section is provided for educational purposes only
 * and to explain why Option A (file-based) is the recommended approach.
 *
 * RISKS:
 * ------
 * - Account suspension (temporary or permanent)
 * - IP address blocking
 * - Legal action from LinkedIn
 * - Violation of terms of service
 * - Bot detection triggering CAPTCHA/2FA challenges
 * - Session cookies expire frequently
 * - LinkedIn actively detects and blocks automation
 *
 * WHEN TO CONSIDER (AUTHORIZED CONTEXTS ONLY):
 * --------------------------------------------
 * - Authorized penetration testing of your own accounts
 * - Security research in controlled lab environments
 * - Educational demonstrations with throwaway accounts
 * - Internal testing (NOT production)
 *
 * TECHNICAL APPROACH (REFERENCE ONLY):
 * -----------------------------------
 *
 * Dependencies needed:
 * ```bash
 * npm install puppeteer puppeteer-extra puppeteer-extra-plugin-stealth
 * npm install puppeteer-extra-plugin-recaptcha
 * ```
 *
 * Skeleton implementation (DO NOT USE WITHOUT AUTHORIZATION):
 * ```javascript
 *
 * const puppeteer = require('puppeteer-extra');
 * const StealthPlugin = require('puppeteer-extra-plugin-stealth');
 * const RecaptchaPlugin = require('puppeteer-extra-plugin-recaptcha');
 *
 * puppeteer.use(StealthPlugin());
 * puppeteer.use(RecaptchaPlugin({
 *   provider: { id: '2captcha', token: 'YOUR_API_KEY' }
 * }));
 *
 * async function postToLinkedInUNOFFICIAL(content, sessionCookies) {
 *   // ⚠️  UNAUTHORIZED - EDUCATIONAL REFERENCE ONLY ⚠️
 *
 *   const browser = await puppeteer.launch({
 *     headless: false, // LinkedIn detects headless mode
 *     args: [
 *       '--no-sandbox',
 *       '--disable-setuid-sandbox',
 *       '--disable-web-security',
 *       '--disable-features=IsolateOrigins,site-per-process'
 *     ]
 *   });
 *
 *   const page = await browser.newPage();
 *
 *   // Set viewport to look like real browser
 *   await page.setViewport({ width: 1920, height: 1080 });
 *
 *   // Set realistic user agent
 *   await page.setUserAgent(
 *     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
 *   );
 *
 *   // Load session cookies (must be obtained manually)
 *   // Cookies expire frequently and require re-authentication
 *   await page.setCookie(...sessionCookies);
 *
 *   try {
 *     // Navigate to LinkedIn
 *     await page.goto('https://www.linkedin.com/feed/', {
 *       waitUntil: 'networkidle2'
 *     });
 *
 *     // Check if logged in (cookies might be expired)
 *     const isLoggedIn = await page.$('.share-box-feed-entry__trigger');
 *     if (!isLoggedIn) {
 *       throw new Error('Not logged in - cookies expired or invalid');
 *     }
 *
 *     // Random delay to mimic human behavior
 *     await page.waitForTimeout(2000 + Math.random() * 3000);
 *
 *     // Click "Start a post" button
 *     await page.click('.share-box-feed-entry__trigger');
 *
 *     // Wait for post modal
 *     await page.waitForSelector('.ql-editor', { timeout: 5000 });
 *
 *     // Random delay
 *     await page.waitForTimeout(1000 + Math.random() * 2000);
 *
 *     // Type content with realistic typing speed
 *     const editor = await page.$('.ql-editor');
 *     await editor.click();
 *
 *     // Type character by character with random delays
 *     for (const char of content) {
 *       await page.keyboard.type(char);
 *       await page.waitForTimeout(50 + Math.random() * 150);
 *     }
 *
 *     // Random delay before posting
 *     await page.waitForTimeout(2000 + Math.random() * 3000);
 *
 *     // Click post button
 *     const postButton = await page.$('[data-test-share-actions="post"]');
 *     await postButton.click();
 *
 *     // Wait for post to complete
 *     await page.waitForTimeout(3000);
 *
 *     // Verify post was created
 *     const success = await page.$('.feed-shared-update-v2');
 *
 *     await browser.close();
 *
 *     return {
 *       success: !!success,
 *       message: success ? 'Posted successfully' : 'Post may have failed'
 *     };
 *
 *   } catch (error) {
 *     await browser.close();
 *     throw new Error(`Automation failed: ${error.message}`);
 *   }
 * }
 *
 * // HOW TO GET SESSION COOKIES (MANUAL PROCESS):
 * // 1. Open LinkedIn in Chrome
 * // 2. Open DevTools (F12)
 * // 3. Go to Application > Cookies > https://www.linkedin.com
 * // 4. Copy these cookies:
 * //    - li_at (most important)
 * //    - JSESSIONID
 * //    - liap
 * //    - li_theme
 * // 5. Cookies expire every 2-4 weeks
 * // 6. Each login from new IP may trigger security challenge
 *
 * const exampleCookies = [
 *   {
 *     name: 'li_at',
 *     value: 'YOUR_LI_AT_COOKIE_VALUE',
 *     domain: '.linkedin.com',
 *     path: '/',
 *     httpOnly: true,
 *     secure: true
 *   },
 *   {
 *     name: 'JSESSIONID',
 *     value: 'YOUR_JSESSIONID_VALUE',
 *     domain: '.www.linkedin.com',
 *     path: '/',
 *     httpOnly: true,
 *     secure: true
 *   }
 * ];
 *
 * // USAGE (UNAUTHORIZED):
 * // await postToLinkedInUNOFFICIAL("Hello LinkedIn!", exampleCookies);
 * ```
 *
 * CHALLENGES YOU WILL FACE:
 * -------------------------
 * 1. Bot Detection:
 *    - LinkedIn uses sophisticated bot detection
 *    - Headless browsers are easily detected
 *    - Even with stealth plugins, detection is possible
 *    - Unusual activity patterns trigger security alerts
 *
 * 2. Authentication:
 *    - Session cookies expire frequently
 *    - New IP addresses trigger security challenges
 *    - 2FA/CAPTCHA will block automation
 *    - No reliable way to handle all auth flows
 *
 * 3. DOM Changes:
 *    - LinkedIn's HTML structure changes frequently
 *    - Selectors break without warning
 *    - A/B tests mean different users see different DOM
 *    - Requires constant maintenance
 *
 * 4. Rate Limiting:
 *    - Aggressive rate limits for suspicious activity
 *    - Even legitimate automation gets flagged
 *    - Temporary blocks escalate to permanent bans
 *
 * 5. Legal/Ethical:
 *    - Violates Terms of Service (Section 8.2)
 *    - LinkedIn has sued companies for scraping/automation
 *    - Not worth the risk for production systems
 *
 * BETTER ALTERNATIVES:
 * -------------------
 * 1. Use Option A (file-based) - implemented in this server
 * 2. Apply for official LinkedIn API access
 * 3. Use LinkedIn's Marketing Developer Platform (for companies)
 * 4. Use Zapier/Make.com (they have official partnerships)
 * 5. Use Buffer/Hootsuite (official LinkedIn partners)
 *
 * CONCLUSION:
 * ----------
 * Option A (file-based) is the recommended approach because:
 * - Zero risk of account suspension
 * - Fully compliant with LinkedIn ToS
 * - Works reliably without maintenance
 * - Perfect for demos, hackathons, MVPs
 * - Can upgrade to official API later
 * - Human review ensures quality control
 *
 * If you absolutely need automation and can't get official API access:
 * - Consider using official partner tools (Buffer, Hootsuite, etc.)
 * - Use throwaway test accounts only
 * - Accept the risk of account bans
 * - Don't use for production/client accounts
 * - Be prepared for constant maintenance
 *
 * Remember: The best code is code that doesn't get your account banned.
 *
 * ==============================================================================
 */
