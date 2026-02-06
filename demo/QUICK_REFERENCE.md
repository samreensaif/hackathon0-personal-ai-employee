# 🎯 Silver Tier Demo - Quick Reference Card

Print this or keep it on a second monitor during recording!

---

## 🚀 Launch Commands

### Windows
```batch
cd demo
silver_tier_demo.bat
```

### Linux/Mac
```bash
cd demo
./silver_tier_demo.sh
```

### Dry-Run Mode
```bash
./silver_tier_demo.sh --dry-run  # No actual actions
```

---

## 📋 Demo Flow (6 Minutes)

| Step | Time  | What Happens | Key Message |
|------|-------|--------------|-------------|
| **Intro** | 0:00 | Banner display | "Production-ready AI automation" |
| **Setup** | 0:30 | Clean environment | "Enterprise-grade attention to detail" |
| **Watchers** | 1:00 | Start monitoring | "24/7 multi-source ingestion" |
| **Tasks** | 1:30 | Create test files | "Multiple input channels" |
| **Categorize** | 2:00 | AI analysis | "Intelligent automation" |
| **Approval** | 2:30 | Generate requests | "Human-in-the-loop control" |
| **Approve** | 3:00 | Manual review | "You're in charge" |
| **Execute** | 3:30 | MCP actions | "Reliable execution" |
| **Briefing** | 4:00 | Daily report | "Complete visibility" |
| **Dashboard** | 4:30 | Real-time view | "At-a-glance status" |
| **Status** | 5:00 | Logs & health | "Production monitoring" |
| **Cleanup** | 5:30 | Graceful shutdown | "Professional operation" |
| **Conclusion** | 5:45 | Final banner | "Ready for production!" |

---

## 💬 Key Talking Points

### Opening
- "Production-ready AI Employee System"
- "Enterprise-grade automation"
- "Human oversight + AI power"

### Watchers
- "24/7 monitoring"
- "Multi-source ingestion"
- "Filesystem + email + more"

### Categorization
- "Intelligent AI analysis"
- "Automatic organization"
- "Saves hours of manual work"

### Approval Workflow
- "Human-in-the-loop"
- "You're in control"
- "AI recommends, you decide"

### MCP Execution
- "Production-grade reliability"
- "Retry logic + rate limits"
- "Complete auditability"

### Reporting
- "Daily CEO briefings"
- "Real-time dashboards"
- "Full visibility"

### Conclusion
- "All features are real"
- "Open source & customizable"
- "Ready for production"

---

## ⚡ Quick Fixes

### Terminal looks bad
```bash
# Increase font size
# Set to dark theme
# Maximize window
```

### Demo script won't run
```bash
# Windows
cd demo
silver_tier_demo.bat

# Linux/Mac - make executable
chmod +x demo/silver_tier_demo.sh
./silver_tier_demo.sh
```

### Python not found
```bash
# Check Python
python --version  # Windows
python3 --version  # Linux/Mac

# Install if needed
# Download from python.org
```

### Watchers won't start
```bash
# Check watcher manager
python scripts/watcher_manager.py --status

# View configuration
python scripts/watcher_manager.py --config
```

### Tasks not categorizing
```bash
# Check logs
cat AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Restart watchers
python scripts/watcher_manager.py --stop
python scripts/watcher_manager.py
```

---

## 🎨 Visual Cues

### Color Meanings
- 🟢 **Green** = Success, completed
- 🔵 **Blue** = Info, substeps
- 🟡 **Yellow** = Warning, attention needed
- 🔴 **Red** = Error, failed
- 🔷 **Cyan** = Headers, important info
- ⚫ **Dim** = Less important, metadata

### Status Symbols
- ✓ Success
- ✗ Error
- → Info/Direction
- ⚠ Warning
- ● Running
- ○ Stopped

---

## 📊 Metrics to Highlight

### System Capabilities
- **Sources:** 2+ (filesystem, Gmail, more...)
- **Processing:** Real-time (<10s latency)
- **Rate Limits:** 10 actions/hour (configurable)
- **Uptime:** 24/7 with auto-restart
- **Retries:** 3 attempts with exponential backoff

### Task Flow
1. **Ingest** → 2-5 seconds
2. **Categorize** → 5-10 seconds
3. **Generate Plan** → 10-30 seconds
4. **Await Approval** → Human time
5. **Execute** → 2-10 seconds
6. **Complete** → Instant

---

## 🎯 Demo Success Criteria

✅ All watchers started successfully
✅ Tasks detected and categorized
✅ Approval requests generated
✅ At least one action executed
✅ CEO briefing created
✅ Dashboard updated
✅ Logs captured
✅ Clean shutdown

---

## 🚨 Emergency Recovery

### If demo breaks mid-way:

```bash
# 1. Stop everything
python scripts/watcher_manager.py --stop
# Kill any stuck processes

# 2. Clean up
rm -f AI_Employee_Vault/test_*.md
rm -f AI_Employee_Vault/*/test_*.md

# 3. Restart demo
./demo/silver_tier_demo.sh
```

### If need to skip to specific step:

```bash
# Just run the specific script
python scripts/generate_approval.py
python scripts/approval_executor.py --once
python scripts/ceo_briefing_generator.py
python scripts/dashboard_updater.py
```

---

## 🎤 Pronunciation Guide

- **MCP** = "M C P" (spell it out)
- **OAuth** = "oh-auth"
- **API** = "A P I" (spell it out)
- **JSON** = "jay-sawn"
- **CEO** = "C E O" (spell it out)
- **AI** = "A I" (spell it out)

---

## 📝 Backup Script

**If you forget what to say:**

> "This is the AI Employee System Silver Tier. It automatically ingests tasks from multiple sources, intelligently categorizes them, generates action plans for approval, and executes approved actions reliably. All with complete monitoring and reporting. This is production-ready, not a prototype."

---

## ⏱️ Time Checkpoints

- **1:00** - Should be starting watchers
- **2:00** - Should be seeing categorization
- **3:00** - Should be at approval
- **4:00** - Should be at CEO briefing
- **5:00** - Should be at status/logs
- **6:00** - Should be wrapping up

If you're off by more than 30 seconds, adjust pace!

---

## 💡 Pro Tips

1. **Rehearse** at least once before recording
2. **Have water** nearby (no ice - noise!)
3. **Silence notifications** on computer
4. **Close other apps** (CPU/RAM)
5. **Test audio** before recording
6. **Smile while talking** (sounds better!)
7. **Pause** between major steps
8. **Breathe** - you've got this!

---

## 🎬 Recording Checklist

**Before Starting:**
- [ ] Terminal maximized, good font size
- [ ] Recording software ready
- [ ] Audio tested
- [ ] Notifications silenced
- [ ] Script rehearsed
- [ ] Water nearby
- [ ] Environment quiet

**During Recording:**
- [ ] Speak clearly and pace well
- [ ] Point out key features
- [ ] Emphasize production-ready
- [ ] Show enthusiasm
- [ ] Pause for visual processing

**After Recording:**
- [ ] Review footage
- [ ] Check audio quality
- [ ] Verify all steps shown
- [ ] Add timestamps
- [ ] Render and upload

---

## 🌟 Remember

**This is impressive!** You built:
- Multi-source task ingestion ✅
- AI-powered categorization ✅
- Approval workflows ✅
- MCP execution ✅
- CEO reporting ✅
- Real-time monitoring ✅

**Show it with confidence!** 🚀

---

**Good luck! You'll do great! 🎥✨**
