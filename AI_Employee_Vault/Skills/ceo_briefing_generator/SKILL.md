---
name: CEO Briefing Generator
slug: ceo-briefing-generator
description: Analyzes system data to generate executive briefings with metrics, insights, and proactive suggestions
version: 1.0.0
author: AI Employee System
tier: gold
status: active
created: 2026-02-05
last_updated: 2026-02-05
dependencies:
  - task_processor
  - email_handler
  - dashboard_updater
---

# CEO Briefing Generator Skill

## 📋 Purpose

Generate comprehensive executive briefings by analyzing real system data over the past 7 days. Provides high-level metrics, identifies bottlenecks, detects patterns, and generates proactive suggestions for business improvement. Designed for executives who need quick, actionable insights without diving into detailed logs.

---

## ⚡ Triggers

### Automatic Triggers
- **Scheduled:** Monday morning at 8:00 AM (weekly briefing)
- **Scheduled:** End of month (monthly briefing)
- **Event:** After major milestone (e.g., 100 tasks completed)

### Manual Triggers
- **Command:** "Generate CEO briefing"
- **Command:** "Create executive report"
- **Command:** "Show me the weekly summary"
- **Script:** `python scripts/ceo_briefing_generator.py`
- **Script:** `python scripts/ceo_briefing_generator.py --days 7`
- **Script:** `python scripts/ceo_briefing_generator.py --type monthly`

---

## 📥 Inputs

### Data Sources

#### 1. Log Files (Past 7 Days)
```
AI_Employee_Vault/Logs/
├── 2026-02-05.json  → Today's activity
├── 2026-02-04.json  → Yesterday
├── 2026-02-03.json  → ...
├── 2026-02-02.json
├── 2026-02-01.json
├── 2026-01-31.json
└── 2026-01-30.json  → 7 days ago
```

**Extracted Data:**
- Task processing events
- Email actions (drafts, sends, searches)
- Approval requests and executions
- Error events
- Performance metrics

#### 2. Vault Folder Analysis
```
AI_Employee_Vault/
├── Needs_Action/      → Tasks not yet processed
├── High_Priority/     → Urgent tasks
├── Pending_Approval/  → Awaiting human review
├── Approved/          → Approved actions
├── Done/              → Completed tasks
├── Failed/            → Failed attempts
└── Plans/             → Execution plans
```

**Extracted Data:**
- Task age (creation time → now)
- Task metadata (priority, category, status)
- Approval wait times
- Failure reasons

#### 3. Rate Limit Data
```
AI_Employee_Vault/Logs/rate_limits.json
```

**Extracted Data:**
- Email send capacity usage
- Draft creation patterns
- Search frequency
- Resource utilization trends

---

## 📤 Outputs

### Main Output: Executive Briefing Report

**Location:** `AI_Employee_Vault/Reports/CEO_Briefing_YYYY-MM-DD.md`

**Structure:**

```markdown
# Executive Briefing
## Week of January 30 - February 5, 2026

📊 **Report Generated:** February 5, 2026 at 8:00 AM
👤 **Prepared For:** Executive Leadership
📈 **Period:** 7 days (January 30 - February 5)

---

## 📊 Executive Summary

**System Health:** 🟢 Operational (99.8% uptime)

**Key Metrics:**
- **Tasks Processed:** 87 tasks (+23% vs prior week)
- **Completion Rate:** 85.1% (74/87 tasks)
- **Avg Processing Time:** 3.2 minutes (-15% improvement)
- **Automation Rate:** 31% (27 tasks auto-completed)

**Highlights:**
- ✅ Successfully processed 87 tasks across 7 categories
- ✅ Auto-completed 27 tasks (31% automation rate)
- ⚠️ 8 tasks pending approval for >48 hours (bottleneck)
- ❌ 2 tasks failed due to API rate limits

**Bottom Line:** System performing well with 23% increase in throughput.
Main concern: Approval backlog needs attention.

---

## 📈 Performance Metrics

### Task Processing Overview

| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Total Tasks | 87 | 71 | +23% ⬆️ |
| Completed | 74 | 59 | +25% ⬆️ |
| Auto-Completed | 27 | 19 | +42% ⬆️ |
| Pending Approval | 8 | 7 | +14% ⬆️ |
| Failed | 2 | 3 | -33% ⬇️ |
| Avg Time | 3.2 min | 3.8 min | -15% ⬇️ |

### Daily Breakdown

```
Mon  ████████████░░░░  12 tasks
Tue  █████████████████  17 tasks (peak)
Wed  ████████████░░░░  13 tasks
Thu  ██████████░░░░░░  10 tasks
Fri  ████████████████  16 tasks
Sat  ████████░░░░░░░░   8 tasks (low)
Sun  ███████████░░░░░  11 tasks
```

**Insight:** Peak activity on Tuesday/Friday. Weekend volume predictably lower.

---

## 🎯 Task Categories Analysis

### Breakdown by Category

| Category | Count | % of Total | Trend |
|----------|-------|------------|-------|
| Email Operations | 35 | 40.2% | ⬆️ +15% |
| Research Tasks | 18 | 20.7% | ➡️ Stable |
| Client Communications | 14 | 16.1% | ⬆️ +20% |
| Internal Updates | 10 | 11.5% | ⬇️ -10% |
| Data Processing | 7 | 8.0% | ➡️ Stable |
| Other | 3 | 3.4% | ⬇️ -25% |

### Completion by Category

```
Email Operations     ████████████████░░  85% (30/35)
Research Tasks       ███████████████░░░  75% (13/18)
Client Comms         ████████████████░░  88% (12/14)
Internal Updates     ████████████████░░  90% (9/10)
Data Processing      ████████████████░░  86% (6/7)
```

**Top Category:** Email operations dominate at 40% of total volume.

**Highest Completion:** Internal updates at 90% completion rate.

---

## 🚨 Bottlenecks & Concerns

### Critical Issues

#### 1. Approval Backlog ⚠️
**Issue:** 8 tasks stuck in Pending_Approval for >48 hours

**Impact:** Delays client communications, reduces system efficiency

**Affected Tasks:**
- `send_proposal_client_acme.md` - 72 hours old (3 days)
- `send_contract_vendor_beta.md` - 65 hours old
- `send_invoice_client_delta.md` - 52 hours old
- `send_partnership_email.md` - 50 hours old
- ... 4 more

**Root Cause:** Manual approval bottleneck during busy period

**Recommendation:**
- Schedule daily approval review sessions
- Consider auto-approval for low-risk actions (<$500 value)
- Delegate approval authority to department heads

**Estimated Impact:** Could free up 8 hours/week of executive time

---

#### 2. Stale Tasks in Needs_Action 📋
**Issue:** 3 tasks sitting in Needs_Action for >7 days

**Tasks:**
- `research_competitor_analysis.md` - 10 days old
- `update_company_policies.md` - 8 days old
- `organize_q1_files.md` - 7 days old

**Root Cause:** Low priority, no urgency markers, not auto-scheduled

**Recommendation:**
- Set automatic escalation after 7 days
- Assign explicit deadlines to all research tasks
- Archive or close truly low-priority tasks

---

#### 3. Failed Task Pattern ❌
**Issue:** 2 tasks failed with same error (API rate limit)

**Tasks:**
- `send_bulk_newsletter.md` - Failed 3 times
- `categorize_archived_emails.md` - Failed 2 times

**Root Cause:** Email API rate limit (10 sends/hour) exceeded

**Recommendation:**
- Implement queue system for bulk operations
- Spread bulk tasks across off-peak hours
- Consider upgrading API tier for higher limits

---

### Performance Concerns

#### Email Response Time Increase
**Observation:** Average time from draft to send increased 40%

**Data:**
- Last Week: 2.3 hours average
- This Week: 3.2 hours average (+39%)

**Analysis:** Likely caused by approval backlog (see Issue #1)

**Impact:** Potential client satisfaction risk

---

#### Weekend Processing Drop
**Observation:** Saturday processing only 47% of weekday average

**Data:**
- Weekday Avg: 14.5 tasks/day
- Saturday: 8 tasks
- Sunday: 11 tasks

**Analysis:** Expected pattern, but some automated tasks could run 24/7

**Opportunity:** Enable weekend auto-processing for routine tasks

---

## 💡 Proactive Suggestions

### Automation Opportunities

#### 1. Automate Recurring Email Drafts
**Observation:** "Weekly status update" email drafted 4 times this week

**Current Process:** Manual draft creation each time

**Suggested Automation:**
- Create email template for weekly updates
- Auto-populate with data from Dashboard
- Schedule draft creation every Friday 3pm
- Requires only approval, not drafting

**Estimated Time Savings:** 30 minutes/week

---

#### 2. Auto-Categorize Research Tasks
**Observation:** Research tasks appear 18 times this week

**Pattern Detected:**
- 100% contain keywords: "research", "analyze", "investigate"
- 88% are medium priority
- 75% can be auto-scheduled for next business day

**Suggested Automation:**
- Auto-route to dedicated "Research" folder
- Auto-assign to research assistant role
- Set default deadline: +2 business days

**Estimated Time Savings:** 45 minutes/week

---

#### 3. Batch Invoice Emails
**Observation:** 7 separate invoice emails sent this week

**Current Process:** Individual approval for each invoice

**Suggested Automation:**
- Collect invoices throughout week
- Bundle into single approval request
- Batch send on Fridays
- Reduces approvals from 7 to 1 per week

**Estimated Time Savings:** 20 minutes/week

**Risk Reduction:** Fewer approval interruptions

---

### Client Focus Areas

#### Client "Acme Corp" Needs Attention
**Observation:** 3 pending tasks all related to Acme Corp

**Tasks:**
- Proposal email (pending approval 72 hours)
- Follow-up research (needs action 4 days)
- Contract review (pending approval 52 hours)

**Risk:** Potential dissatisfaction from delayed responses

**Action Items:**
1. Prioritize Acme Corp approval requests today
2. Batch-process all Acme-related tasks this week
3. Schedule check-in call with Acme stakeholder

---

#### Client "Beta Inc" High Activity
**Observation:** 8 tasks related to Beta Inc this week (9% of total)

**Activity Type:**
- 5 email communications
- 2 research requests
- 1 contract update

**Analysis:** Likely in active project phase

**Suggestion:**
- Dedicate resource to Beta Inc account
- Create Beta Inc task template for consistency
- Set up weekly sync meeting

---

### Process Improvements

#### 1. Implement Task Aging Policy
**Rationale:** 3 tasks >7 days old without progress

**Suggested Policy:**
- Day 3: Automatic reminder
- Day 7: Escalate to high priority
- Day 14: Force review or archive

**Expected Outcome:** No tasks languish beyond 2 weeks

---

#### 2. Two-Tier Approval System
**Rationale:** All approvals currently require executive review

**Suggested Tiers:**
- **Tier 1 (Low Risk):** Auto-approve or delegate
  - Emails <500 words
  - Recipients on whitelist
  - Standard templates

- **Tier 2 (High Risk):** Executive approval required
  - New client communications
  - Contracts/legal docs
  - Financial transactions >$1000

**Expected Outcome:** 60% of approvals can be Tier 1

---

#### 3. Weekend Automation Schedule
**Rationale:** Weekend volume drop represents opportunity

**Suggested Schedule:**
- Saturday 9am: Auto-process routine research tasks
- Saturday 2pm: Auto-categorize inbox
- Sunday 11am: Generate weekly prep report
- Sunday 5pm: Auto-draft Monday status emails

**Expected Outcome:** Smoother Monday morning, proactive preparation

---

## 📊 Detailed Analytics

### Task Velocity Trends

```
Week 1: ████████████░░░░░░░░  65 tasks
Week 2: █████████████░░░░░░░  71 tasks (+9%)
Week 3: ████████████████░░░░  87 tasks (+23%)
Week 4: [Current Week]
```

**Trajectory:** Strong upward trend in task volume (+23% week-over-week)

**Projection:** If trend continues, expect ~100 tasks next week

**Capacity Analysis:** Current system can handle ~120 tasks/week before strain

**Recommendation:** Monitor closely; consider resource expansion if >100 tasks sustained

---

### Email Operations Deep Dive

#### Volume by Action Type

| Action | This Week | Capacity Used | Notes |
|--------|-----------|---------------|-------|
| Drafts Created | 28 | 11% (28/250) | Well below limit |
| Emails Sent | 7 | 10% (7/70) | Healthy usage |
| Searches Performed | 15 | 2% (15/700) | Minimal usage |
| Emails Categorized | 3 batches (187 emails) | - | Efficient |

**Insight:** Email system operating at low capacity utilization. Plenty of headroom.

---

#### Response Time Distribution

```
< 1 hour   ██████░░░░░░░░░░░░  6 emails (20%)
1-4 hours  ████████████░░░░░░  12 emails (40%)
4-8 hours  ████████░░░░░░░░░░  8 emails (27%)
8-24 hours ████░░░░░░░░░░░░░░  3 emails (10%)
> 24 hours ██░░░░░░░░░░░░░░░░  1 email (3%)
```

**Median Response:** 3.2 hours (acceptable)

**Outlier:** 1 email took 28 hours due to approval delay

---

### Approval Pattern Analysis

#### Approval Time by Day

```
Mon: 2.1 hours avg
Tue: 1.8 hours avg (fastest)
Wed: 3.5 hours avg
Thu: 4.2 hours avg
Fri: 5.1 hours avg (slowest)
Sat: No approvals
Sun: No approvals
```

**Pattern:** Approval times increase as week progresses

**Hypothesis:** Friday approval fatigue + end-of-week rush

**Recommendation:** Block Friday morning for approval session

---

## 🎯 Action Items for Leadership

### Immediate (This Week)

1. **⚠️ URGENT: Clear Approval Backlog**
   - Review 8 pending approvals >48 hours
   - Prioritize client communications
   - Target: Clear by end of day
   - Owner: Executive

2. **📋 Review Stale Tasks**
   - Decide on 3 tasks >7 days old
   - Archive or set explicit deadlines
   - Target: Decision by Friday
   - Owner: Operations Manager

3. **❌ Fix Failed Task Blockers**
   - Address API rate limit issue
   - Implement queue for bulk operations
   - Target: Resolve by end of week
   - Owner: Technical Lead

---

### Short Term (Next 2 Weeks)

4. **🤖 Implement Automation #1: Weekly Email Templates**
   - Create templates for recurring emails
   - Set up auto-draft schedule
   - Estimated effort: 2 hours
   - Owner: Operations

5. **📊 Establish Two-Tier Approval System**
   - Define low-risk criteria
   - Set up delegation rules
   - Train team on new process
   - Estimated effort: 4 hours
   - Owner: Executive + Operations

6. **🔍 Client Account Review: Acme Corp**
   - Process 3 pending Acme tasks
   - Schedule stakeholder check-in
   - Document account status
   - Estimated effort: 1 hour
   - Owner: Account Manager

---

### Long Term (Next 30 Days)

7. **📈 Implement Task Aging Policy**
   - Document escalation rules
   - Configure automated reminders
   - Test with pilot group
   - Estimated effort: 6 hours
   - Owner: Operations Manager

8. **🔄 Optimize Weekend Processing**
   - Identify tasks suitable for weekend automation
   - Configure scheduler
   - Monitor for issues
   - Estimated effort: 3 hours
   - Owner: Technical Lead

9. **📊 Monthly Executive Dashboard**
   - Set up automated monthly briefing
   - Include trend analysis
   - Add industry benchmarks
   - Estimated effort: 8 hours
   - Owner: Analytics Team

---

## 📈 Success Metrics

### KPIs to Monitor

**Operational Efficiency:**
- Task completion rate >85% (current: 85.1% ✓)
- Average processing time <4 minutes (current: 3.2 min ✓)
- Automation rate >30% (current: 31% ✓)

**Responsiveness:**
- Approval wait time <24 hours (current: 58 hours avg ❌)
- Email response time <4 hours (current: 3.2 hours ✓)
- Task age in Needs_Action <7 days (current: 8.3 days avg ❌)

**Quality:**
- Failed task rate <5% (current: 2.3% ✓)
- Client satisfaction >4.5/5 (manual survey)
- Rework rate <10% (manual tracking)

---

## 📊 Appendix: Raw Data Summary

### Task Log Summary (7 Days)

```json
{
  "period": "2026-01-30 to 2026-02-05",
  "total_tasks": 87,
  "completed": 74,
  "pending": 11,
  "failed": 2,
  "categories": {
    "email_operations": 35,
    "research": 18,
    "client_comms": 14,
    "internal": 10,
    "data": 7,
    "other": 3
  },
  "daily_breakdown": {
    "2026-02-05": 17,
    "2026-02-04": 13,
    "2026-02-03": 10,
    "2026-02-02": 16,
    "2026-02-01": 11,
    "2026-01-31": 8,
    "2026-01-30": 12
  }
}
```

---

**Report End**

---

*This briefing was automatically generated by the AI Employee System.*
*For questions or details, contact: system-admin@company.com*
*Next briefing: February 12, 2026*
```

---

## 🎯 Capabilities

This skill provides comprehensive executive analysis capabilities:

1. **Multi-Day Log Analysis**
   - Scans Logs/ directory for past 7-30 days
   - Parses JSON log entries for task events
   - Aggregates metrics across time periods
   - Calculates daily, weekly, and monthly trends

2. **Performance Metrics Calculation**
   - Completion rate (target: >85%)
   - Automation rate (target: >30%)
   - Average processing time
   - Success/failure rates
   - Week-over-week comparisons

3. **Bottleneck Detection**
   - Identifies approvals >48 hours
   - Detects stale tasks >7 days in Needs_Action
   - Flags delayed high priority tasks >24 hours
   - Calculates average wait times by folder

4. **Pattern Recognition**
   - High automation rate detection (>40%)
   - Low automation opportunities (<20%)
   - High failure rate concerns (>5%)
   - Category dominance analysis (>40%)
   - Recurring task identification

5. **Proactive Suggestion Generation**
   - Automation opportunities for recurring tasks
   - Bottleneck resolution recommendations
   - Process improvement suggestions
   - Client focus area identification
   - Priority-ranked action items with impact estimates

6. **Executive Report Generation**
   - Markdown formatted for readability
   - Non-technical language for executives
   - Visual indicators (🟢 🟡 🔴)
   - ASCII charts for trends
   - JSON data appendix for technical review

---

## 📋 Process Flow

### High-Level Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. COLLECT DATA                                             │
│    - Scan Logs/ for past 7 days                            │
│    - Read vault folders for task ages                      │
│    - Load rate limit data                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ANALYZE LOGS                                             │
│    - Parse JSON entries                                     │
│    - Extract task events                                    │
│    - Categorize by type                                     │
│    - Calculate completion/automation rates                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. DETECT BOTTLENECKS                                       │
│    - Check approval wait times (>48h threshold)             │
│    - Identify stale tasks (>7 days)                         │
│    - Flag high priority delays (>24h)                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. IDENTIFY PATTERNS                                        │
│    - Detect automation opportunities                        │
│    - Find recurring tasks                                   │
│    - Analyze category distributions                         │
│    - Spot efficiency trends                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. GENERATE SUGGESTIONS                                     │
│    - Create actionable recommendations                      │
│    - Calculate estimated savings                            │
│    - Prioritize by impact (high/medium/low)                 │
│    - Categorize by type (automation/bottleneck/process)     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. RENDER REPORT                                            │
│    - Generate executive summary                             │
│    - Create performance metrics tables                      │
│    - Build bottleneck analysis section                      │
│    - Format suggestion list                                 │
│    - Add action items timeline                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. SAVE & REPORT                                            │
│    - Write to Reports/CEO_Briefing_YYYY-MM-DD.md            │
│    - Log generation event                                   │
│    - Return success status with metrics                     │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Steps

**Step 1: Data Collection (5-10 seconds)**
```python
# Scan Logs/ directory
log_files = scan_logs_directory(days=7)

# Load and parse each log
logs_data = []
for log_file in log_files:
    with open(log_file, 'r') as f:
        logs_data.append(json.load(f))

# Scan vault folders for task ages
task_ages = scan_vault_folders()
```

**Step 2: Analysis (2-5 seconds)**
```python
# Calculate metrics
total_tasks = count_total_tasks(logs_data)
completed = count_completed_tasks(logs_data)
completion_rate = (completed / total_tasks) * 100

auto_completed = count_auto_tasks(logs_data)
automation_rate = (auto_completed / total_tasks) * 100
```

**Step 3: Bottleneck Detection (1-2 seconds)**
```python
# Check approval times
approval_bottlenecks = []
for task in pending_approvals:
    age_hours = calculate_age_hours(task)
    if age_hours > 48:
        approval_bottlenecks.append(task)
```

**Step 4: Pattern Detection (1-2 seconds)**
```python
# Detect patterns
patterns = []
if automation_rate > 40:
    patterns.append({"type": "positive", "msg": "High automation"})
if automation_rate < 20:
    patterns.append({"type": "opportunity", "msg": "Low automation"})
```

**Step 5: Suggestion Generation (2-3 seconds)**
```python
# Generate suggestions
suggestions = []
if automation_rate < 30:
    suggestions.append({
        "title": f"Increase Automation by {30 - automation_rate}%",
        "priority": "MEDIUM",
        "savings": calculate_savings(30 - automation_rate)
    })
```

**Step 6: Report Rendering (1-2 seconds)**
```python
# Render markdown report
report = render_executive_summary(metrics)
report += render_performance_metrics(metrics)
report += render_bottlenecks(bottlenecks)
report += render_suggestions(suggestions)
```

**Step 7: Save Report (<1 second)**
```python
# Write to file
output_path = f"AI_Employee_Vault/Reports/CEO_Briefing_{date}.md"
with open(output_path, 'w') as f:
    f.write(report)
```

**Total Time:** 10-25 seconds for 7 days of data

---

## 📚 Example Usage

### Example 1: Weekly Briefing Generation (Standard)

**User Request:**
```
"Generate a CEO briefing for the past week"
```

**Claude Response:**
```
I'll generate an executive briefing analyzing the past 7 days of data.

[Runs: python scripts/ceo_briefing_generator.py]

✅ CEO Briefing generated successfully!

📊 **Summary:**
- Analyzed 11 tasks from February 5, 2026
- Completion Rate: 100.0% ✅
- Automation Rate: 18.2% (below target)
- 0 bottlenecks detected
- 1 proactive suggestion generated

📍 **Report Location:**
AI_Employee_Vault/Reports/CEO_Briefing_2026-02-05.md

🎯 **Key Insight:**
System is healthy with excellent completion rate. Main opportunity:
increase automation from 18.2% to 30%+ to save an estimated 24
minutes per week.

Would you like me to open the report or explain any of the findings?
```

**Generated Report Preview:**
```markdown
# Executive Briefing
## January 29 - February 05, 2026

**System Health:** 🟢 Excellent

**Key Metrics:**
- Tasks Processed: 11 tasks
- Completion Rate: 100.0%
- Automation Rate: 18.2%
- Failed Tasks: 0

**Bottom Line:** System performing well.
```

---

### Example 2: Custom Time Period Analysis

**User Request:**
```
"Show me a 14-day executive briefing"
```

**Command:**
```bash
python scripts/ceo_briefing_generator.py --days 14
```

**Output:**
```
============================================================
CEO Briefing Generator
============================================================

Analyzing data for the past 14 days...

[1/5] Analyzing log files...
      Found 87 tasks across 14 days

[2/5] Analyzing task ages...
      Identified 3 approval bottlenecks

[3/5] Detecting patterns...
      Detected 4 patterns

[4/5] Generating suggestions...
      Generated 3 actionable suggestions

[5/5] Rendering report...

[OK] Report generated: AI_Employee_Vault\Reports\CEO_Briefing_2026-02-05.md

============================================================
BRIEFING SUMMARY
============================================================
Total Tasks Analyzed:  87
Completion Rate:       85.1%
Automation Rate:       29.3%
Bottlenecks Found:     3
Suggestions Generated: 3
============================================================
```

---

### Example 3: Addressing Bottlenecks

**Scenario:** Report shows 3 approval bottlenecks

**User Action:**
```
"What are the approval bottlenecks from the briefing?"
```

**Claude Response:**
```
Based on the latest CEO briefing (2026-02-05), here are the 3
approval bottlenecks detected:

🚨 **Approval Bottlenecks (>48 hours)**

1. **email_client_a.md**
   - Action: Send email to Client A
   - Wait Time: 72 hours (3 days)
   - Created: February 2, 2026
   - Priority: HIGH
   - Risk: Client communication delay

2. **contract_review.md**
   - Action: Review contract terms
   - Wait Time: 58 hours
   - Created: February 3, 2026
   - Priority: MEDIUM

3. **budget_approval.md**
   - Action: Approve Q1 budget
   - Wait Time: 51 hours
   - Created: February 3, 2026
   - Priority: HIGH

📋 **Recommendation from Briefing:**
Schedule a 30-minute approval session today to clear the backlog.
This will unblock 3 high-value tasks and prevent client
dissatisfaction.

Would you like me to:
1. Open these files for review?
2. Execute approved actions?
3. Set up an approval workflow?
```

---

### Example 4: Acting on Suggestions

**Briefing Suggestion:**
```markdown
### 1. 🟡 Increase Automation Rate by 12%

**Type:** Automation
**Priority:** MEDIUM
**Description:** Current: 18.2%, Target: 30.0%
**Recommendation:** Review task types for automation opportunities
**Estimated Savings:** 24 minutes/week
```

**User Request:**
```
"Help me implement the automation suggestion from the briefing"
```

**Claude Response:**
```
I'll help you increase the automation rate from 18.2% to 30%+.

📊 **Analysis from Briefing:**
- Current automation: 2 of 11 tasks (18.2%)
- Target: 3-4 tasks automated (30%+)
- Potential savings: 24 minutes/week

🎯 **Action Plan:**

1. **Identify Automation Candidates**
   - I'll analyze the 11 tasks to find recurring patterns
   - Look for simple, rule-based tasks

2. **Create Automation Rules**
   - Add keyword triggers for auto-completion
   - Create templates for common tasks

3. **Test Automation**
   - Run test cases
   - Measure improvement

Would you like me to:
A) Analyze the tasks to find automation candidates
B) Show me the task breakdown from the briefing
C) Create automation rules directly

Choose A, B, or C (or describe what you'd prefer).
```

---

### Example 5: Scheduled Weekly Briefing

**Setup (One-Time):**
```bash
# Windows Task Scheduler
# Task: CEO Briefing Generator
# Trigger: Every Monday at 8:00 AM
# Action: python D:\project\scripts\ceo_briefing_generator.py
```

**Automated Execution (Monday 8:00 AM):**
```
============================================================
CEO Briefing Generator (Scheduled)
============================================================

Analyzing data for the past 7 days...

[1/5] Analyzing log files...
      Found 124 tasks across 7 days

[2/5] Analyzing task ages...
      Identified 0 approval bottlenecks

[3/5] Detecting patterns...
      Detected 3 patterns

[4/5] Generating suggestions...
      Generated 2 actionable suggestions

[5/5] Rendering report...

[OK] Report generated: AI_Employee_Vault\Reports\CEO_Briefing_2026-02-10.md

============================================================
BRIEFING SUMMARY
============================================================
Total Tasks Analyzed:  124
Completion Rate:       91.9%
Automation Rate:       35.5%
Bottlenecks Found:     0
Suggestions Generated: 2
============================================================

System Health: 🟢 Excellent
Report ready for Monday morning review.
```

**Executive Workflow:**
1. Check email notification (optional setup)
2. Open `Reports/CEO_Briefing_2026-02-10.md`
3. Review 2-minute executive summary
4. Check action items section
5. Delegate or address high-priority suggestions

---

## 🎯 Analysis Components

### 1. Log Analysis (Past 7 Days)

**Function:** `analyze_logs(days=7) → Dict`

**Process:**
1. Scan `Logs/` directory for past 7 days
2. Load and parse each JSON log file
3. Extract task processing events
4. Categorize by action type
5. Calculate daily metrics
6. Identify patterns and trends

**Metrics Calculated:**
- Total tasks processed per day
- Tasks by category (email, research, client, etc.)
- Completion rate per day
- Average processing time
- Failed tasks count and reasons
- Peak activity times

---

### 2. Task Age Analysis

**Function:** `analyze_task_ages() → Dict`

**Process:**
1. Scan all vault folders
2. Read metadata from each task file
3. Calculate age (creation date → now)
4. Identify stale tasks (>7 days)
5. Flag approval bottlenecks (>48 hours)

**Bottlenecks Detected:**
- Pending Approval >48 hours: Critical concern
- Needs Action >7 days: Review needed
- High Priority >24 hours: Urgent attention
- Failed >3 attempts: Systematic issue

---

### 3. Performance Metrics

**Function:** `calculate_performance_metrics() → Dict`

**Metrics:**
- **Task Velocity:** Tasks/day, week-over-week change
- **Completion Rate:** (Completed / Total) × 100%
- **Automation Rate:** (Auto-completed / Total) × 100%
- **Avg Processing Time:** Median time from creation to completion
- **Success Rate:** (Total - Failed) / Total × 100%
- **Approval Wait Time:** Time in Pending_Approval

**Comparison:**
- This week vs last week
- Daily patterns (Monday vs Friday)
- Category-specific rates

---

### 4. Pattern Detection

**Function:** `detect_patterns() → List[Dict]`

**Patterns Identified:**
- Recurring tasks (same title/keywords appear 5+ times)
- Client focus (tasks from same client)
- Time patterns (peak days, slow days)
- Category trends (increasing/decreasing volume)
- Failure patterns (same error repeated)

---

### 5. Suggestion Generation

**Function:** `generate_suggestions() → List[Dict]`

**Categories:**

**Automation Opportunities:**
- Recurring task detection
- Template candidates
- Batch processing opportunities

**Process Improvements:**
- Bottleneck solutions
- Policy recommendations
- Resource allocation

**Client Focus:**
- High-activity clients
- Delayed responses
- Satisfaction risks

---

## 💻 Code Reference

### Main Implementation

**File:** `scripts/ceo_briefing_generator.py`

**Key Functions:**

```python
def generate_ceo_briefing(days: int = 7, output_type: str = "weekly") -> Dict:
    """
    Main function to generate CEO briefing.

    Args:
        days: Number of days to analyze (default: 7)
        output_type: 'weekly', 'monthly', or 'custom'

    Returns:
        {
            'success': bool,
            'report_file': str,
            'metrics': dict,
            'suggestions': list
        }
    """
    pass


def analyze_logs(days: int = 7) -> Dict:
    """
    Analyze log files for past N days.

    Returns:
        {
            'total_tasks': int,
            'daily_breakdown': dict,
            'category_breakdown': dict,
            'completion_rate': float,
            'failed_tasks': list
        }
    """
    pass


def analyze_task_ages() -> Dict:
    """
    Analyze age of tasks in all folders.

    Returns:
        {
            'stale_tasks': list,
            'approval_bottlenecks': list,
            'avg_age_by_folder': dict
        }
    """
    pass


def calculate_performance_metrics(log_data: Dict) -> Dict:
    """
    Calculate performance metrics from log data.

    Returns:
        {
            'completion_rate': float,
            'automation_rate': float,
            'avg_processing_time': float,
            'velocity_trend': str,
            'week_over_week_change': float
        }
    """
    pass


def detect_patterns(log_data: Dict) -> List[Dict]:
    """
    Detect patterns in task data.

    Returns:
        [
            {
                'pattern_type': 'recurring_task',
                'description': 'Weekly status email',
                'frequency': 4,
                'suggestion': 'Automate with template'
            },
            ...
        ]
    """
    pass


def generate_suggestions(analysis: Dict) -> List[Dict]:
    """
    Generate proactive suggestions.

    Returns:
        [
            {
                'type': 'automation',
                'priority': 'high',
                'title': 'Automate Weekly Email',
                'description': '...',
                'estimated_savings': '30 min/week'
            },
            ...
        ]
    """
    pass


def render_briefing(data: Dict) -> str:
    """
    Render briefing markdown from analysis data.

    Returns:
        Complete markdown report string
    """
    pass
```

---

## ⚙️ Configuration

### Analysis Parameters

**File:** `config/briefing_config.json`

```json
{
  "analysis": {
    "default_days": 7,
    "bottleneck_thresholds": {
      "approval_hours": 48,
      "needs_action_days": 7,
      "high_priority_hours": 24
    },
    "pattern_detection": {
      "min_recurrence": 3,
      "similarity_threshold": 0.8
    }
  },
  "metrics": {
    "target_completion_rate": 85.0,
    "target_automation_rate": 30.0,
    "target_approval_hours": 24,
    "target_processing_minutes": 4.0
  },
  "report": {
    "include_raw_data": true,
    "include_charts": true,
    "executive_summary_length": "medium",
    "detail_level": "high"
  }
}
```

### Suggestion Templates

**File:** `templates/briefing_suggestions.json`

```json
{
  "automation": {
    "recurring_task": {
      "title": "Automate Recurring Task: {task_name}",
      "description": "This task appears {frequency} times per week. Consider creating a template and auto-scheduling.",
      "estimated_savings": "{minutes} minutes/week"
    },
    "batch_processing": {
      "title": "Batch Process {task_type}",
      "description": "{count} tasks of type '{task_type}' processed individually. Batching could reduce overhead.",
      "estimated_savings": "{percentage}% time reduction"
    }
  },
  "bottleneck": {
    "approval_delay": {
      "title": "Approval Backlog: {count} Tasks >48 Hours",
      "description": "Consider delegation or auto-approval for low-risk items.",
      "impact": "Delays client communications, reduces efficiency"
    },
    "stale_tasks": {
      "title": "{count} Tasks Stale in Needs_Action",
      "description": "Tasks older than 7 days need review or archival.",
      "recommendation": "Implement aging policy with auto-escalation"
    }
  },
  "client_focus": {
    "high_activity": {
      "title": "Client {client_name} High Activity",
      "description": "{count} tasks this week ({percentage}% of total)",
      "suggestion": "Dedicate resource or create account-specific workflow"
    },
    "delayed_response": {
      "title": "Client {client_name} Delayed Responses",
      "description": "{count} pending tasks, longest wait: {hours} hours",
      "risk": "Potential dissatisfaction",
      "action": "Prioritize and process today"
    }
  }
}
```

---

## 🛡️ Error Handling

### 1. Missing Log Files

**Scenario:** Some log files don't exist for requested period

**Handling:**
```python
try:
    with open(log_file) as f:
        logs = json.load(f)
except FileNotFoundError:
    # Continue with available data
    print(f"Warning: Log file {log_file} not found, skipping")
    continue
```

**Report Note:** "Analysis based on X of Y days (Y-X days missing logs)"

---

### 2. Malformed Data

**Scenario:** Log file has corrupted JSON or missing fields

**Handling:**
- Skip corrupted entries
- Use default values for missing fields
- Note in report: "X entries skipped due to data quality"

---

### 3. Insufficient Data

**Scenario:** Less than 2 days of log data available

**Handling:**
- Generate limited report
- Mark metrics as "Insufficient data"
- Provide advisory: "Minimum 2 days recommended for meaningful analysis"

---

## 📊 Success Criteria

Briefing is valuable when:

- ✅ Identifies at least 2 actionable bottlenecks
- ✅ Generates at least 3 proactive suggestions
- ✅ Provides week-over-week comparisons
- ✅ Flags critical issues (>48 hour delays)
- ✅ Estimates time savings from suggestions
- ✅ Includes executive summary (<200 words)
- ✅ Readable by non-technical executives
- ✅ Generated in <30 seconds
- ✅ Saved to Reports/ folder
- ✅ Auto-formats dates and metrics

---

## 🔗 Related Skills

### Current
- **Dashboard Updater** - Provides real-time data
- **Task Processor** - Generates log data
- **Email Handler** - Tracks email metrics

### Future
- **Trend Analyzer** - Historical trend analysis
- **Benchmark Comparison** - Industry standards
- **Predictive Analytics** - Forecast future load
- **Alert System** - Real-time critical alerts

---

## 📞 Support

### Documentation
- **This Skill:** `AI_Employee_Vault/Skills/ceo_briefing_generator/SKILL.md`
- **Implementation:** `scripts/ceo_briefing_generator.py`
- **Templates:** `templates/briefing_*.json`

### Testing
```bash
# Generate weekly briefing
python scripts/ceo_briefing_generator.py

# Generate for specific period
python scripts/ceo_briefing_generator.py --days 7

# Generate monthly briefing
python scripts/ceo_briefing_generator.py --type monthly

# Dry run (no file write)
python scripts/ceo_briefing_generator.py --dry-run
```

---

## 🚀 Roadmap

### Version 1.0 (Current)
- [x] 7-day log analysis
- [x] Task age detection
- [x] Bottleneck identification
- [x] Pattern detection
- [x] Suggestion generation
- [x] Markdown report output

### Version 1.1 (Planned)
- [ ] Month-over-month comparisons
- [ ] Client satisfaction scoring
- [ ] ROI calculations for suggestions
- [ ] Visual charts (ASCII or external)
- [ ] Email delivery of briefing
- [ ] Custom date ranges

### Version 2.0 (Future)
- [ ] Predictive analytics
- [ ] Industry benchmarking
- [ ] Interactive web report
- [ ] Natural language queries
- [ ] ML-based pattern detection
- [ ] Auto-pilot mode (implement suggestions automatically)

---

**Skill Version:** 1.0.0
**Status:** Active ✓
**Last Updated:** February 2026
**Production Ready:** Yes
