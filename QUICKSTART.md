# 🚀 Quick Start Guide - Silver Tier

Get up and running with the Personal AI Employee in under 5 minutes!

---

## ⚡ 30-Second Setup

```bash
# 1. Navigate to project directory
cd hackathon0-personal-ai-employee

# 2. Run the launcher
python launch_silver.py
```

That's it! The menu will guide you through everything.

---

## 🎯 3-Minute Demo

### Step 1: Create Test Tasks (30 seconds)

```bash
python test_silver_tier.py
```

This creates 7 sample tasks demonstrating all categories.

### Step 2: Start the Watcher (10 seconds)

From the menu, select `[1]` or run:

```bash
python watchers/inbox_watcher_silver.py
```

Wait 6-9 seconds for automatic processing.

### Step 3: Check Results (1 minute)

Press `Ctrl+C` to stop the watcher, then explore:

```bash
AI_Employee_Vault/
├── Done/              ← Check auto-completed tasks! ✅
├── High_Priority/     ← Check urgent tasks! ⚠️
├── Pending_Approval/  ← Check sensitive tasks! 🔒
├── Needs_Action/      ← Check normal tasks! 📋
└── Plans/             ← Check execution plans! 📝
```

### Step 4: Generate Briefing (30 seconds)

From the menu, select `[3]` or run:

```bash
python scripts/generate_briefing.py
```

Check the report in `AI_Employee_Vault/Reports/`

---

## 📚 What Just Happened?

**The system automatically:**

1. **Detected** 7 task files you created
2. **Moved** them from vault root → Inbox → Needs_Action
3. **Added** metadata (timestamps, status, source)
4. **Categorized** each task by content:
   - 2 tasks auto-completed → `Done/`
   - 3 tasks flagged for approval → `Pending_Approval/`
   - 1 task marked urgent → `High_Priority/`
   - 1 task stayed for processing → `Needs_Action/`
5. **Created** execution plans for each in `Plans/`
6. **Logged** all actions to `Logs/YYYY-MM-DD.json`
7. **Generated** CEO briefing with metrics

**Total time:** < 10 seconds
**Human intervention:** Zero!

---

## 🎓 Understanding Task Categories

### ✅ Auto-Complete → Done/

**Example Task:**
```markdown
# Reminder
FYI - Review the report when available.
```

**What happens:**
- Detected keywords: "reminder", "fyi"
- No approval keywords found
- Auto-completed to `Done/`
- Plan marked as completed
- **You don't need to do anything!**

---

### ⚠️ High Priority → High_Priority/

**Example Task:**
```markdown
# URGENT: Server Issue
CRITICAL production issue - needs immediate attention ASAP!
```

**What happens:**
- Detected keywords: "urgent", "critical", "immediate", "asap"
- Moved to `High_Priority/`
- Flagged with ⚠️ emoji
- **You should address this today!**

---

### 🔒 Approval Required → Pending_Approval/

**Example Task:**
```markdown
# Send Payment
Process payment to vendor for invoice #12345
```

**What happens:**
- Detected keywords: "send", "payment"
- Moved to `Pending_Approval/`
- Held for your review
- **You must approve before execution!**

---

### 📋 Normal Priority → Needs_Action/

**Example Task:**
```markdown
# Update Documentation
Update the user guide with new screenshots this week.
```

**What happens:**
- No special keywords detected
- Stays in `Needs_Action/`
- Standard workflow
- **Address in normal timeframe**

---

## 🔄 Daily Workflow

### Morning (5 minutes)

```bash
# 1. Generate briefing
python scripts/generate_briefing.py

# 2. Review High_Priority/ folder
#    → Address urgent items first

# 3. Review Pending_Approval/ folder
#    → Approve or reject sensitive tasks

# 4. Check Done/ folder
#    → Verify auto-completed tasks are correct
```

### During Day (Continuous)

```bash
# Start the watcher
python watchers/inbox_watcher_silver.py

# Drop task files as they come in
# System processes automatically
# You work on what matters
```

### End of Day (2 minutes)

```bash
# Stop watcher (Ctrl+C)

# Check Logs/ for daily activity
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Review completion status
# Plan for tomorrow
```

---

## 📝 Creating Your Own Tasks

### Method 1: Drop Markdown Files

Create a `.md` file in `AI_Employee_Vault/` root:

```markdown
# My Task Title

Description of what needs to be done.

Include any relevant details here.
```

Save and let the watcher pick it up!

### Method 2: Use Inbox Folder

Drop files directly into `AI_Employee_Vault/Inbox/`:

```bash
echo "# Quick Task\nSomething to do later" > AI_Employee_Vault/Inbox/task.md
```

### Method 3: Programmatic Creation

```python
from pathlib import Path

task = """# Automated Task
Created by script
"""

Path("AI_Employee_Vault/mytask.md").write_text(task)
```

---

## 🎯 Tips for Best Results

### ✅ DO:

1. **Use clear keywords:**
   - "URGENT" for high priority
   - "FYI" or "reminder" for auto-complete
   - "send email" or "payment" for approval

2. **Be specific in task descriptions:**
   - Include deadlines
   - List action items
   - Provide context

3. **Review the briefings:**
   - Check weekly for patterns
   - Adjust workflow based on metrics
   - Monitor automation rate

4. **Check auto-completed tasks:**
   - Verify system categorized correctly
   - Adjust keywords if needed
   - Move files if miscategorized

### ❌ DON'T:

1. **Don't use ambiguous titles:**
   - Bad: "Thing to do"
   - Good: "Send Q1 report to client"

2. **Don't ignore High_Priority folder:**
   - Check it daily
   - Address items promptly

3. **Don't let approvals pile up:**
   - Review Pending_Approval/ regularly
   - Approve or reject decisively

4. **Don't skip the briefings:**
   - They show system health
   - Identify bottlenecks early

---

## 🛠️ Troubleshooting

### Problem: Tasks not moving automatically

**Solution:**
```bash
# Check if watcher is running
# You should see output every few seconds

# If not running, start it:
python watchers/inbox_watcher_silver.py
```

---

### Problem: Task miscategorized

**Solution:**
```bash
# Manually move the file:
mv AI_Employee_Vault/Done/task.md AI_Employee_Vault/Needs_Action/

# Then adjust keywords in task content
# Or adjust KEYWORDS in runner_silver.py
```

---

### Problem: Briefing shows no data

**Solution:**
```bash
# Check if log files exist:
ls -la AI_Employee_Vault/Logs/

# Process some tasks first:
python scripts/runner_silver.py

# Then generate briefing:
python scripts/generate_briefing.py
```

---

### Problem: Watcher not auto-processing

**Solution:**

Check `watchers/inbox_watcher_silver.py` line 18:

```python
AUTO_PROCESS = True  # Should be True
```

If False, change to True and restart watcher.

---

## 📊 Understanding the Logs

Log files in `AI_Employee_Vault/Logs/YYYY-MM-DD.json`:

```json
[
  {
    "timestamp": "2026-02-04T20:30:00",
    "action": "auto_complete",
    "file": "reminder_task.md",
    "details": {
      "plan": "reminder_task_plan.md",
      "category": "auto_complete",
      "priority": "low"
    }
  }
]
```

**Action Types:**
- `move_to_inbox`: File entered system
- `move_to_needs_action`: File ready for processing
- `auto_complete`: Task auto-completed ✅
- `requires_approval`: Task needs approval 🔒
- `high_priority`: Urgent task identified ⚠️
- `categorized`: Normal task processed 📋
- `error`: Something went wrong ❌

---

## 🎓 Next Steps

### Beginner
1. ✅ Complete 3-minute demo
2. ✅ Create 3 custom tasks
3. ✅ Generate first briefing
4. ✅ Review all folders

### Intermediate
1. Customize keywords in `runner_silver.py`
2. Adjust polling interval in watcher
3. Create task templates
4. Set up daily briefing schedule

### Advanced
1. Integrate with email (forward → task)
2. Add Slack notifications
3. Create custom workflows
4. Build API endpoints
5. Extend to Gold Tier features

---

## 📚 Documentation Reference

- **[README.md](README.md)** - Project overview
- **[README_SILVER.md](README_SILVER.md)** - Complete Silver Tier docs
- **[FEATURES_SILVER.md](FEATURES_SILVER.md)** - Feature comparison
- **[QUICKSTART.md](QUICKSTART.md)** - This file

---

## 🎉 You're Ready!

You now have a fully functional AI Employee that can:

- ✅ Auto-complete 40-60% of tasks
- ✅ Route sensitive tasks for approval
- ✅ Flag urgent items for immediate attention
- ✅ Generate executive briefings
- ✅ Track everything with metadata
- ✅ Log all activity for auditing

**Time to completion:** < 5 minutes
**Learning curve:** Low
**Value delivered:** High
**Cost:** Free (Python standard library only)

---

## 💬 Need Help?

1. Check the documentation files
2. Review log files in `Logs/`
3. Examine execution plans in `Plans/`
4. Test with `test_silver_tier.py`
5. Use menu launcher for guided experience

---

**🚀 Happy Automating!**

*Personal AI Employee - Silver Tier*
*Making task management effortless*

