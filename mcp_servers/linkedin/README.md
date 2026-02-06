# LinkedIn MCP Server

**Safe, file-based LinkedIn integration for the AI Employee system.**

---

## ⚠️ Important Notice

This MCP server uses a **file-based approach** for safety and compliance:

### Why File-Based?

1. **LinkedIn API Restrictions**
   - Official LinkedIn Marketing Developer Platform requires company approval
   - Strict compliance requirements
   - Limited to approved applications only

2. **Safety First**
   - No risk of account suspension
   - No API violations
   - No unauthorized automation

3. **Audit Trail**
   - All drafts tracked in files
   - Easy to review before posting
   - Compliance-friendly

4. **Perfect for Hackathons/Demos**
   - Works immediately without API approval
   - Shows intent and workflow
   - Production-ready architecture

### For Production Automation

To automate LinkedIn posting in production:

1. **Apply for API Access**
   - Visit: https://www.linkedin.com/developers/
   - Apply for Marketing Developer Platform
   - Wait for approval (can take weeks)

2. **Alternative: Browser Automation** (Use with caution!)
   - See `AUTOMATION_WARNING.md` for details
   - Risk of account suspension
   - Not recommended for production

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to linkedin directory
cd mcp_servers/linkedin

# Install dependencies
npm install

# Test server
npm test
```

### Configuration

No configuration needed! The server uses file-based drafts automatically.

**Folders created:**
- `AI_Employee_Vault/LinkedIn_Drafts/` - Draft posts
- `AI_Employee_Vault/Logs/` - Activity logs

---

## 📊 Features

### 1. Create LinkedIn Post Draft

Creates a validated draft with suggestions:

```javascript
{
  "tool": "create_linkedin_post",
  "arguments": {
    "content": "Excited to share our latest AI innovation! 🚀\n\nWe've built an autonomous employee that can handle emails, tasks, and reporting. Check it out!\n\n#AI #Innovation #Productivity",
    "schedule_time": "2026-02-06T09:00:00Z",
    "tags": ["product-launch", "ai"]
  }
}
```

**Returns:**
- Draft ID
- Validation results
- Suggested hashtags
- Best posting times
- Rate limit status
- File paths (JSON + Markdown)

### 2. Content Validation

Validates content without creating draft:

```javascript
{
  "tool": "validate_linkedin_content",
  "arguments": {
    "content": "Your post content here..."
  }
}
```

**Checks:**
- Length (max 3000 characters)
- Hashtag count (recommends ≤5)
- URL count (recommends ≤2)
- Engagement optimization
- Best practices compliance

### 3. Get Draft Status

Check draft details:

```javascript
{
  "tool": "get_draft_status",
  "arguments": {
    "draft_id": "li_1234567890_a1b2c3d4"
  }
}
```

### 4. List Drafts

View all drafts:

```javascript
{
  "tool": "list_linkedin_drafts",
  "arguments": {
    "status": "draft"  // Optional: "draft", "posted", "archived"
  }
}
```

### 5. Posting Recommendations

Get best times to post:

```javascript
{
  "tool": "get_posting_recommendations",
  "arguments": {}
}
```

**Returns:**
- Best posting times (UTC)
- Engagement tips
- Weekend vs weekday advice
- Current rate limit status

---

## 📋 Rate Limiting

Built-in rate limiting to match LinkedIn best practices:

- **Posts:** 1 per hour, 3 per day
- **Drafts:** Unlimited (reasonable use)

Rate limits tracked in: `AI_Employee_Vault/Logs/linkedin_rate_limits.json`

---

## 📝 Draft Files

### JSON Format

**Location:** `AI_Employee_Vault/LinkedIn_Drafts/li_*.json`

```json
{
  "draftId": "li_1234567890_a1b2c3d4",
  "createdAt": "2026-02-05T18:30:00.000Z",
  "status": "draft",
  "content": "Your post content...",
  "metadata": {
    "validation": {
      "valid": true,
      "errors": [],
      "warnings": [],
      "stats": {
        "length": 245,
        "hashtags": 3,
        "urls": 1,
        "mentions": 0
      }
    },
    "suggestedHashtags": ["#AI", "#Innovation", "#Productivity"],
    "bestPostingTimes": {
      "recommendations": [...],
      "tip": "Best engagement on weekdays..."
    }
  },
  "posting": {
    "method": "manual",
    "instructions": [...]
  }
}
```

### Markdown Format

**Location:** `AI_Employee_Vault/LinkedIn_Drafts/li_*.md`

Human-readable format with:
- Post content
- Suggested hashtags
- Content warnings
- Statistics
- Posting instructions
- Best times to post

---

## 🎯 Content Guidelines

### Length

- **Min:** 150 characters (recommended)
- **Sweet spot:** 150-300 characters
- **Max:** 3000 characters
- **Long posts:** >1500 characters (consider articles instead)

### Hashtags

- **Recommended:** 3-5 hashtags
- **Maximum:** 30 hashtags
- **Placement:** End of post or inline

### URLs

- **Recommended:** 1-2 URLs
- **Multiple URLs:** May reduce engagement

### Best Posting Times

**Weekdays (UTC):**
- 8:00 AM - Morning check-ins
- 9:00 AM - Start of workday
- 12:00 PM - Lunch break
- 5:00 PM - End of workday
- 6:00 PM - Evening check-ins

**Weekends (UTC):**
- 10:00 AM - Late morning
- 11:00 AM - Mid-morning
- 3:00 PM - Afternoon

---

## 🔄 Workflow

### Creating a Post

1. **AI creates draft**
   ```javascript
   create_linkedin_post({
     content: "Post content...",
     schedule_time: "2026-02-06T09:00:00Z"
   })
   ```

2. **Draft saved to files**
   - JSON: `LinkedIn_Drafts/li_*.json`
   - Markdown: `LinkedIn_Drafts/li_*.md`

3. **Human reviews draft**
   - Open markdown file
   - Review content and suggestions
   - Make any edits

4. **Human posts manually**
   - Copy content to LinkedIn
   - Post at recommended time
   - Add any images/media

5. **Update draft status**
   - Edit JSON file
   - Set `status: "posted"`
   - Add `postedAt` timestamp
   - Add `postUrl` (optional)

---

## 📊 Hashtag Suggestions

The server suggests hashtags based on content analysis:

### Categories

- **Business:** #Business #Entrepreneurship #Leadership #Strategy
- **Technology:** #Technology #AI #MachineLearning #SoftwareDevelopment
- **Marketing:** #Marketing #DigitalMarketing #ContentMarketing #Branding
- **Career:** #Career #JobSearch #Hiring #CareerAdvice
- **Productivity:** #Productivity #TimeManagement #WorkLifeBalance
- **Finance:** #Finance #Investing #FinTech #Economics
- **Sales:** #Sales #B2B #SaaS #CustomerSuccess

### How It Works

1. Analyzes post content for keywords
2. Matches to relevant categories
3. Suggests top 5 hashtags
4. Avoids over-tagging

---

## 📈 Analytics & Tracking

### Logs

All actions logged to: `AI_Employee_Vault/Logs/YYYY-MM-DD.json`

**Example log entry:**
```json
{
  "timestamp": "2026-02-05T18:30:00.000Z",
  "source": "linkedin_mcp",
  "action": "draft_created",
  "draftId": "li_1234567890_a1b2c3d4",
  "contentLength": 245,
  "hashtags": 3,
  "warnings": []
}
```

### Rate Limits

Tracked in: `AI_Employee_Vault/Logs/linkedin_rate_limits.json`

```json
{
  "posts": [
    "2026-02-05T18:30:00.000Z",
    "2026-02-05T20:15:00.000Z"
  ],
  "drafts": [
    "2026-02-05T18:30:00.000Z",
    "2026-02-05T19:00:00.000Z"
  ]
}
```

---

## 🔧 Integration Examples

### With Task Processor

```python
# Task: "Create LinkedIn post about our new feature"
from mcp_client import call_tool

result = call_tool('create_linkedin_post', {
    'content': post_content,
    'tags': ['feature-launch']
})

# Result includes draft ID and file paths
draft_id = result['draftId']
markdown_path = result['readablePath']

# Create approval request
create_approval_request({
    'action': 'linkedin_post',
    'draft_id': draft_id,
    'preview': markdown_path
})
```

### With Approval Workflow

```python
# In approval executor
if action == 'linkedin_post':
    draft_id = metadata['draft_id']

    # Get draft details
    draft = call_tool('get_draft_status', {
        'draft_id': draft_id
    })

    # Show preview to human
    display_draft_preview(draft)

    # Wait for manual posting
    instructions = draft['posting']['instructions']
    display_instructions(instructions)
```

---

## 🚀 Future Automation (When API Approved)

### Option B: Official API Integration

When LinkedIn API access is approved:

1. **Replace file-based posting**
   ```javascript
   // Add OAuth2 configuration
   const oauth2Client = new OAuth2Client(
     process.env.LINKEDIN_CLIENT_ID,
     process.env.LINKEDIN_CLIENT_SECRET,
     redirect_uri
   );

   // Implement actual posting
   async function publishPost(content) {
     const response = await linkedinAPI.posts.create({
       author: 'urn:li:person:xxxxx',
       lifecycleState: 'PUBLISHED',
       specificContent: {
         'com.linkedin.ugc.ShareContent': {
           shareCommentary: { text: content },
           shareMediaCategory: 'NONE'
         }
       }
     });
     return response;
   }
   ```

2. **Keep validation and recommendations**
   - Content validation still useful
   - Hashtag suggestions still valuable
   - Best times still relevant

3. **Add scheduling**
   - Queue posts for future publishing
   - Respect rate limits
   - Retry failed posts

### Option C: Browser Automation (Risky!)

⚠️ **NOT RECOMMENDED** - See `AUTOMATION_WARNING.md`

If you must automate without API approval (at your own risk):

1. **Use Puppeteer/Playwright**
   ```javascript
   const puppeteer = require('puppeteer');

   async function postToLinkedIn(content) {
     const browser = await puppeteer.launch({ headless: false });
     const page = await browser.newPage();

     // Load session cookies
     await page.setCookie(...cookies);

     // Navigate to LinkedIn
     await page.goto('https://www.linkedin.com');

     // Click post button
     await page.click('[aria-label="Start a post"]');

     // Enter content
     await page.type('[aria-label="Text editor"]', content);

     // Post
     await page.click('[aria-label="Post"]');

     await browser.close();
   }
   ```

2. **Risks:**
   - Account suspension
   - CAPTCHA challenges
   - Session invalidation
   - Terms of Service violation

3. **If you proceed:**
   - Use with test account first
   - Add delays between actions (human-like)
   - Rotate user agents
   - Handle CAPTCHA
   - Accept risk of ban

---

## 📞 Support

### Documentation

- **This README:** Setup and usage
- **AUTOMATION_WARNING.md:** Risks of automation
- **API Documentation:** https://docs.microsoft.com/en-us/linkedin/

### Troubleshooting

**Issue:** Drafts not created

**Check:**
```bash
# Verify directories
ls AI_Employee_Vault/LinkedIn_Drafts/

# Check logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json | jq '.[] | select(.source=="linkedin_mcp")'
```

**Issue:** Rate limit hit

**Check:**
```bash
cat AI_Employee_Vault/Logs/linkedin_rate_limits.json | jq '.'
```

**Reset rate limits:**
```bash
# Delete rate limit file (use with caution!)
rm AI_Employee_Vault/Logs/linkedin_rate_limits.json
```

---

## 🎯 Best Practices

1. **Content Quality**
   - Use validation before creating drafts
   - Follow hashtag recommendations
   - Post at recommended times

2. **Workflow**
   - Review drafts before posting
   - Update status after posting
   - Track what works (engagement)

3. **Rate Limiting**
   - Respect the 1 post/hour limit
   - Space out posts throughout day
   - Quality over quantity

4. **Compliance**
   - Never use unofficial automation
   - Keep audit trail
   - Follow LinkedIn Terms of Service

---

## 📚 Related

- **Email MCP:** `mcp_servers/email/`
- **Task Processor:** `scripts/runner_silver.py`
- **Approval System:** `scripts/approval_executor.py`

---

**Version:** 1.0.0
**Type:** File-Based (Safe)
**Status:** Production Ready
**Last Updated:** 2026-02-05
