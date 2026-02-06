# AI Employee Skills System

Welcome to the Skills Registry! This directory contains all available skills for the AI Employee system.

---

## 🔍 Quick Start

### View All Skills
See the complete, auto-generated registry:
- **[SKILLS_INDEX.md](SKILLS_INDEX.md)** - Full list with descriptions, use cases, and categories

### Validate Skills
Ensure all skills meet quality standards:
```bash
python scripts/validate_skills.py
```

### Create New Skill
Follow the template in any existing skill's `SKILL.md` file, then run the validator.

---

## 📚 Available Skills

For the complete, up-to-date list of all skills with full details, see **[SKILLS_INDEX.md](SKILLS_INDEX.md)**.

### Quick Overview

1. **Task Processor** (🥈 Silver) - Analyzes and categorizes tasks intelligently
2. **Email Handler** (🥈 Silver) - Gmail integration with approval workflow
3. **Dashboard Updater** (🥈 Silver) - Real-time system status dashboard
4. **CEO Briefing Generator** (🥇 Gold) - Executive analytics and insights

---

## 🚀 Using Skills

### Via Claude Code
```
"Use the task processor skill"
"Generate a CEO briefing"
"Draft an email to john@example.com"
```

### Via Scripts
```bash
python scripts/runner_silver.py          # Task Processor
python scripts/email_handler.py          # Email Handler
python scripts/dashboard_updater.py      # Dashboard Updater
python scripts/ceo_briefing_generator.py # CEO Briefing
```

---

## ✅ Validation

The skills validator (`scripts/validate_skills.py`) checks all skills for:
- Valid YAML frontmatter with required fields
- All required documentation sections
- Proper version formatting
- Valid status and tier values
- No broken references to scripts or files

**Run validation:**
```bash
# Full validation + regenerate index
python scripts/validate_skills.py

# Check only (no index update)
python scripts/validate_skills.py --check-only

# Verbose output
python scripts/validate_skills.py --verbose
```

---

## 🔧 Creating New Skills

1. Create directory: `AI_Employee_Vault/Skills/my_skill/`
2. Create `SKILL.md` with required frontmatter and sections
3. Implement code in `scripts/` if needed
4. Add examples in `examples/` subdirectory
5. Run validator: `python scripts/validate_skills.py`
6. Index auto-updates with your skill

**Required Sections in SKILL.md:**
- Purpose
- Triggers (automatic and manual)
- Inputs (format and structure)
- Outputs (location and format)
- Process Flow or Capabilities
- Example Usage
- Code Reference
- Configuration
- Error Handling

**Use any existing skill as a template!**

---

## 📊 Skill Tiers

- **🥉 Bronze** - Basic functionality, single purpose
- **🥈 Silver** - Enhanced features, multiple capabilities
- **🥇 Gold** - Advanced features, comprehensive analysis
- **💎 Platinum** - Mission-critical, enterprise-grade

---

## 📈 Skill Status

- **✅ Active** - Production-ready, fully tested
- **🚧 Development** - In progress, may be incomplete
- **📋 Planned** - Designed but not implemented
- **⚠️ Deprecated** - No longer maintained

---

## 📞 Support

- **Full Registry:** See [SKILLS_INDEX.md](SKILLS_INDEX.md)
- **Validation:** Run `python scripts/validate_skills.py --verbose`
- **Templates:** Use any existing skill's `SKILL.md` as reference
- **Logs:** Check `AI_Employee_Vault/Logs/` for execution history

---

**Maintained by:** AI Employee System
**Last Generated:** Auto-updated by validator
**Version:** 1.0.0

---

### 3. Dashboard Updater (dashboard_updater/)

**Version:** 1.0.0
**Status:** Active ✓

**What it does:**
- Maintains real-time Dashboard.md
- Counts tasks in all folders
- Shows recent activity feed
- Displays system health status
- Lists approval queue with ages
- Calculates completion rates
- Provides actionable next steps

**Triggers:**
- After task processor runs
- After email actions
- After approval execution
- Manual: "Update the dashboard"

**Documentation:** [dashboard_updater/SKILL.md](dashboard_updater/SKILL.md)

---

### 4. CEO Briefing Generator (ceo_briefing_generator/)

**Version:** 1.0.0
**Status:** Active ✓
**Tier:** Gold

**What it does:**
- Analyzes logs for past 7 days
- Calculates performance metrics
- Identifies bottlenecks (>48h approvals, >7d stale)
- Detects patterns and trends
- Generates proactive suggestions
- Creates executive markdown reports

**Triggers:**
- Scheduled: Monday 8am (weekly)
- Manual: "Generate CEO briefing"
- Command: `python scripts/ceo_briefing_generator.py`

**Documentation:** [ceo_briefing_generator/SKILL.md](ceo_briefing_generator/SKILL.md)

---

## 🎯 Skill Structure

Each skill follows this structure:

```
Skills/
└── skill_name/
    ├── SKILL.md              # Skill definition
    ├── README.md             # Usage guide
    ├── implementation/       # Code files
    │   └── skill.py
    ├── tests/                # Tests
    │   └── test_skill.py
    └── examples/             # Usage examples
        └── example.md
```

---

## 📖 Skill Definition Format

Each `SKILL.md` includes:

```yaml
---
name: Skill Name
slug: skill-name
description: Brief description
version: 1.0.0
author: Author Name
tier: bronze|silver|gold
status: active|development|deprecated
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
---

# Skill Name

## Purpose
[What the skill does]

## Triggers
[When the skill activates]

## Inputs
[What data it requires]

## Outputs
[What it produces]

## Process Flow
[Step-by-step execution]

## Example Usage
[Real examples with Claude interactions]

## Code Reference
[Links to implementation files]

## Configuration
[Settings and customization]

## Error Handling
[How errors are managed]
```

---

## 🚀 Using Skills

### With Claude Code

```bash
# List available skills
claude

# In conversation:
> "Use the task processor skill on pending tasks"
> "Run task processor"
> "Process all tasks in Needs_Action"
```

### Manual Execution

```bash
# Task processor
python scripts/runner_silver.py

# Direct script execution
python AI_Employee_Vault/Skills/task_processor/implementation/process.py
```

### API Integration

```python
from AI_Employee_Vault.Skills.task_processor import TaskProcessorSkill

skill = TaskProcessorSkill()
result = skill.execute(input_data)
```

---

## 🔧 Creating New Skills

### Step 1: Create Skill Directory

```bash
mkdir -p AI_Employee_Vault/Skills/my_skill/{implementation,tests,examples}
```

### Step 2: Create SKILL.md

```bash
cp AI_Employee_Vault/Skills/task_processor/SKILL.md \
   AI_Employee_Vault/Skills/my_skill/SKILL.md
# Edit to match your skill
```

### Step 3: Implement

```python
# AI_Employee_Vault/Skills/my_skill/implementation/skill.py

class MySkill:
    """Skill implementation."""

    def execute(self, inputs):
        """Execute the skill."""
        pass
```

### Step 4: Add Tests

```python
# AI_Employee_Vault/Skills/my_skill/tests/test_skill.py

def test_my_skill():
    skill = MySkill()
    result = skill.execute(test_input)
    assert result['success'] is True
```

### Step 5: Document

```markdown
# AI_Employee_Vault/Skills/my_skill/README.md

## Usage

...examples...
```

---

## 📊 Skill Categories

### Task Management Skills
- ✅ **Task Processor** - Categorize and route tasks
- 🔲 **Priority Escalator** - Auto-escalate overdue tasks
- 🔲 **Task Scheduler** - Schedule delayed execution

### Communication Skills
- ✅ **Email Handler** - Draft, send, search, categorize emails
- 🔲 **Meeting Scheduler** - Find meeting times
- 🔲 **Slack Notifier** - Send team notifications

### Data Skills
- ✅ **Dashboard Updater** - Real-time metrics and status
- ✅ **CEO Briefing Generator** - Executive insights from real data
- 🔲 **Data Analyzer** - Deep dive analytics
- 🔲 **Search Aggregator** - Search across systems

### Automation Skills
- ✅ **Approval Executor** - Execute approved actions
- 🔲 **Workflow Runner** - Multi-step workflows
- 🔲 **Backup Manager** - Automated backups

---

## 🎓 Best Practices

### 1. Clear Triggers

Define exactly when skill activates:
```yaml
triggers:
  - file_event: Needs_Action/*.md
  - command: "process tasks"
  - schedule: "*/5 * * * *"  # Every 5 minutes
```

### 2. Detailed Documentation

Include examples with:
- Input data
- Processing steps
- Output results
- Claude interactions

### 3. Error Handling

Always handle:
- Invalid inputs
- Missing files
- API failures
- Timeout errors

### 4. Logging

Log all activities:
```python
log_entry = {
    'timestamp': datetime.now().isoformat(),
    'skill': 'task_processor',
    'action': 'categorize',
    'success': True
}
```

### 5. Testing

Test coverage should be >80%:
- Unit tests for functions
- Integration tests for workflow
- Mock external dependencies

---

## 📈 Metrics

Track skill performance:

```json
{
  "skill": "task_processor",
  "executions": 1234,
  "success_rate": 98.5,
  "avg_duration": 2.3,
  "last_executed": "2026-02-05T10:30:00"
}
```

---

## 🔗 Integration

Skills integrate with:

- **Watchers** - Trigger skills on file events
- **Processors** - Use skills for task handling
- **MCP Servers** - Execute external actions
- **Dashboard** - Display skill activity
- **Logs** - Record execution history
- **API** - REST endpoints for skills

---

## 📞 Support

- **Skill Development:** See individual skill README.md
- **General Help:** See main project documentation
- **Issues:** Create GitHub issue with [skill:name] tag

---

## 🎉 Available Now

✅ **Task Processor** - Full featured, production ready
✅ **Email Handler** - Gmail MCP integration, approval workflow
✅ **Dashboard Updater** - Real-time system metrics and status
✅ **CEO Briefing Generator** - Executive insights from real data

Coming soon:
- Priority Escalator
- Workflow Runner
- Email Template Manager
- Trend Analyzer

---

**Last Updated:** February 2026
**Total Skills:** 4 active, 5 planned
**Status:** Growing ecosystem 🌱
