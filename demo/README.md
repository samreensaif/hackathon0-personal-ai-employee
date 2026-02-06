# Silver Tier Demo Scripts

Professional demo scripts to showcase all Silver Tier features of the AI Employee System.

## 🎬 Demo Features

This demo showcases:

1. **Multi-Source Task Ingestion**
   - Filesystem inbox watcher
   - Gmail inbox watcher
   - Automatic task detection

2. **Intelligent Task Categorization**
   - Priority detection (High, Medium, Low)
   - Category classification (Email, Social Media, etc.)
   - Automatic folder organization

3. **Approval Workflow**
   - Automatic approval request generation
   - Human-in-the-loop oversight
   - Plan generation for complex tasks

4. **MCP Action Execution**
   - Email sending via Gmail MCP
   - LinkedIn posting
   - Retry logic with exponential backoff
   - Rate limiting (10 actions/hour)

5. **CEO Briefing Generation**
   - Daily summary of completed tasks
   - System status overview
   - Performance metrics

6. **Dashboard Updates**
   - Real-time status display
   - Task counts by category
   - System health indicators

## 🚀 Quick Start

### Windows

```batch
cd demo
silver_tier_demo.bat
```

### Linux/Mac

```bash
cd demo
chmod +x silver_tier_demo.sh
./silver_tier_demo.sh
```

## 🎥 Recording a Demo Video

The script includes **pause points** throughout for easy video recording:

1. **Run the script** - it will pause at key moments
2. **Explain what's happening** at each pause
3. **Press any key** to continue to the next step
4. **Screenshot points** are clearly marked

### Recommended Video Structure

```
0:00 - Introduction
0:30 - Environment Setup
1:00 - Starting Watchers
1:30 - Creating Test Tasks
2:00 - Task Categorization
2:30 - Approval Workflow
3:00 - Manual Approval
3:30 - MCP Execution
4:00 - CEO Briefing
4:30 - Dashboard Display
5:00 - System Status
5:30 - Conclusion
```

## 🧪 Dry-Run Mode

Test the demo without actually executing actions:

### Windows
```batch
silver_tier_demo.bat --dry-run
```

### Linux/Mac
```bash
./silver_tier_demo.sh --dry-run
```

This will:
- ✅ Show all steps and output
- ✅ Create test files
- ✅ Run categorization
- ❌ NOT send real emails
- ❌ NOT post to LinkedIn
- ❌ NOT execute MCP actions

## 📋 Prerequisites

Ensure you have:

1. **Python 3.8+** installed
2. **Required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **MCP Servers** (optional, for full demo):
   - Gmail MCP server configured
   - LinkedIn MCP server configured
   - See `MCP_CONFIGURATION_GUIDE.md`

4. **Watcher System** configured:
   ```bash
   python scripts/watcher_manager.py --config
   ```

## 🎨 Visual Output

The demo includes:

- ✅ **Color-coded output**
  - 🟢 Green: Success messages
  - 🔵 Blue: Info/substeps
  - 🟡 Yellow: Warnings
  - 🔴 Red: Errors
  - 🔷 Cyan: Headers/info

- ⏰ **Timestamps** on every action
- 📊 **Status indicators** (✓, ✗, →, ⚠)
- 📦 **Boxed headers** for visual sections
- 🎯 **Progress tracking**

## 🗂️ Demo File Structure

```
demo/
├── README.md                    # This file
├── silver_tier_demo.bat        # Windows demo script
├── silver_tier_demo.sh         # Unix/Linux/Mac demo script
└── test_data/                  # Sample test files (created during demo)
    ├── test_email_task.md
    └── test_social_media_task.md
```

## 🔧 Troubleshooting

### Watchers won't start

```bash
# Check Python path
python --version

# Check if watcher_manager exists
ls scripts/watcher_manager.py

# Check configuration
python scripts/watcher_manager.py --config
```

### No tasks are categorized

```bash
# Check watcher logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Verify inbox_watcher is running
python scripts/watcher_manager.py --status
```

### MCP actions fail

```bash
# Check MCP server configuration
cat .mcp.json

# Test in dry-run mode
python scripts/approval_executor.py --dry-run --once
```

### Permissions error (Unix/Mac)

```bash
# Make script executable
chmod +x demo/silver_tier_demo.sh

# Run with explicit bash
bash demo/silver_tier_demo.sh
```

## 🎯 Demo Tips

### For Best Results:

1. **Run in a clean environment** first time
2. **Use a terminal with good color support**
   - Windows: Windows Terminal (recommended)
   - Mac: iTerm2 or Terminal.app
   - Linux: Most modern terminals

3. **Maximize terminal window** for best visibility

4. **Read the prompts** - they explain what's happening

5. **Take your time** - the demo is designed to be paused

### For Video Recording:

1. **Use OBS Studio** or similar screen recorder
2. **Set terminal font size to 14-16pt** for visibility
3. **Use dark theme** for better contrast
4. **Record at 1920x1080** minimum resolution
5. **Include voiceover** explaining each step

## 🔄 Cleanup

The demo will ask if you want to clean up test files at the end.

Manual cleanup:

```bash
# Remove all test files
rm -f AI_Employee_Vault/test_*.md
rm -f AI_Employee_Vault/High_Priority/test_*.md
rm -f AI_Employee_Vault/Pending_Approval/test_*.md
rm -f AI_Employee_Vault/Approved/test_*.md
rm -f AI_Employee_Vault/Done/test_*.md
rm -f AI_Employee_Vault/Plans/test_*_plan.md
```

## 📊 What Gets Created

During the demo, these files are created:

1. **Test Tasks** (in vault root):
   - `test_email_task.md` - Email sending task
   - `test_social_media_task.md` - LinkedIn posting task

2. **Categorized** (moved to High_Priority/):
   - Same files, after categorization

3. **Approval Requests** (in Pending_Approval/):
   - Generated approval request files

4. **Plans** (in Plans/):
   - `test_email_task_plan.md`
   - `test_social_media_task_plan.md`

5. **Completed** (in Done/):
   - Tasks after successful execution

6. **Logs** (in Logs/):
   - `YYYY-MM-DD.json` - Daily log file
   - `rate_limits.json` - Rate limit tracking

7. **Reports** (in Reports/):
   - `CEO_Briefing_YYYY-MM-DD.md` - Daily briefing

8. **Dashboard** (in vault root):
   - `Dashboard.md` - Updated dashboard

## 🎓 Learning Points

After running the demo, you'll understand:

1. **How watchers monitor multiple sources**
2. **How tasks are automatically categorized**
3. **How the approval workflow works**
4. **How MCP actions are executed**
5. **How CEO briefings are generated**
6. **How the system handles errors and retries**
7. **How rate limiting works**
8. **How logging and monitoring works**

## 🚀 Production Readiness

This demo proves the system is ready for:

- ✅ Multi-source task ingestion
- ✅ Intelligent automation with human oversight
- ✅ Reliable MCP action execution
- ✅ Comprehensive monitoring and reporting
- ✅ Error handling and recovery
- ✅ Rate limiting and safety controls

## 📝 Next Steps

After the demo:

1. **Review the code** in the scripts
2. **Customize the watchers** for your needs
3. **Configure MCP servers** for your services
4. **Add your own task types** and categories
5. **Customize the approval workflow**
6. **Add more actions** to the executor

## 💡 Tips for Customization

```python
# Add custom task categories
# Edit: watchers/inbox_watcher_silver.py
CATEGORIES = {
    "email": ["email", "send", "reply"],
    "social": ["post", "tweet", "linkedin"],
    "custom": ["your", "keywords", "here"]  # Add this
}

# Add custom MCP actions
# Edit: scripts/approval_executor.py
def execute_custom_action(self, metadata):
    """Execute your custom action."""
    # Your code here
    pass

# Customize CEO briefing
# Edit: scripts/ceo_briefing_generator.py
def generate_custom_section(self):
    """Add custom section to briefing."""
    # Your code here
    pass
```

## 📞 Support

If you encounter issues:

1. Check the logs in `AI_Employee_Vault/Logs/`
2. Review the documentation in project root
3. Run in `--dry-run` mode to debug
4. Check watcher status: `python scripts/watcher_manager.py --status`

## 🎉 Enjoy the Demo!

This is a production-ready system. The demo shows real functionality, not just mockups!

---

**Ready to transform your workflow with AI? Let's go! 🚀**
