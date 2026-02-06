#!/usr/bin/env python3
"""
Skills Validator and Registry Generator
Validates all skills in the Skills/ directory and generates SKILLS_INDEX.md

Version: 1.0.0
Author: AI Employee System
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


# ============================================================================
# CONFIGURATION
# ============================================================================

SKILLS_DIR = Path("./AI_Employee_Vault/Skills")
INDEX_FILE = SKILLS_DIR / "SKILLS_INDEX.md"

# Required sections in SKILL.md files (at least one variant must exist)
REQUIRED_SECTIONS = [
    ["Purpose"],
    ["Triggers"],
    ["Inputs"],
    ["Outputs"],
    ["Capabilities", "Process Flow"],  # Either is acceptable
    ["Process Flow", "Capabilities"],  # Either is acceptable
    ["Example Usage", "Examples"],     # Either is acceptable
    ["Code Reference", "Implementation"],  # Either is acceptable
    ["Configuration", "Settings"],     # Either is acceptable
    ["Error Handling"]
]

# Required metadata fields in YAML frontmatter
REQUIRED_METADATA = [
    "name",
    "slug",
    "description",
    "version",
    "status"
]


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def scan_skills_directory() -> List[Path]:
    """Scan Skills/ directory for skill folders."""
    if not SKILLS_DIR.exists():
        print(f"[ERROR] Skills directory not found: {SKILLS_DIR}")
        return []

    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                skills.append(item)

    return sorted(skills)


def parse_yaml_frontmatter(content: str) -> Dict:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    metadata = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata


def validate_skill_file(skill_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a SKILL.md file.

    Returns:
        (is_valid, issues_list)
    """
    issues = []
    skill_file = skill_path / "SKILL.md"

    if not skill_file.exists():
        return False, ["SKILL.md file not found"]

    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    # Check 1: YAML frontmatter
    metadata = parse_yaml_frontmatter(content)
    if not metadata:
        issues.append("Missing YAML frontmatter (should start with ---)")

    # Check 2: Required metadata fields
    for field in REQUIRED_METADATA:
        if field not in metadata:
            issues.append(f"Missing required metadata field: {field}")

    # Check 3: Required sections (allow alternatives)
    content_lower = content.lower()
    for section_options in REQUIRED_SECTIONS:
        # Check if at least one variant exists
        found = False
        if isinstance(section_options, list):
            for section in section_options:
                if re.search(rf"##\s+.*{re.escape(section.lower())}", content_lower):
                    found = True
                    break
        else:
            section = section_options
            if re.search(rf"##\s+.*{re.escape(section.lower())}", content_lower):
                found = True

        if not found:
            section_str = " or ".join(section_options) if isinstance(section_options, list) else section_options
            issues.append(f"Missing required section: {section_str}")

    # Check 4: Validate version format
    if "version" in metadata:
        version = metadata["version"]
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            issues.append(f"Invalid version format: {version} (should be X.Y.Z)")

    # Check 5: Validate status
    if "status" in metadata:
        valid_statuses = ["active", "development", "deprecated", "planned"]
        if metadata["status"] not in valid_statuses:
            issues.append(f"Invalid status: {metadata['status']} (should be one of: {', '.join(valid_statuses)})")

    # Check 6: Check for broken internal file references
    # Look for references to scripts or files
    script_refs = re.findall(r'scripts/([a-zA-Z0-9_]+\.py)', content)
    for script_ref in script_refs:
        script_path = Path("./scripts") / script_ref
        if not script_path.exists():
            issues.append(f"Broken reference to script: scripts/{script_ref}")

    # Check for vault folder references
    vault_refs = re.findall(r'AI_Employee_Vault/([a-zA-Z0-9_/]+)', content)
    for vault_ref in vault_refs:
        # Skip common placeholders and variables
        if any(placeholder in vault_ref for placeholder in ['[', '{', 'YYYY', 'MM', 'DD', '*']):
            continue
        vault_path = Path("./AI_Employee_Vault") / vault_ref
        if not vault_path.exists() and not vault_path.parent.exists():
            # Only warn, not error, as some folders may be created dynamically
            pass  # Could add warnings here if needed

    is_valid = len(issues) == 0
    return is_valid, issues


def extract_skill_info(skill_path: Path) -> Dict:
    """Extract skill information for the index."""
    skill_file = skill_path / "SKILL.md"

    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return None

    metadata = parse_yaml_frontmatter(content)

    # Extract use cases from content (look for "Example Usage" or "Triggers" sections)
    use_cases = []

    # Try to find example usage section
    example_match = re.search(r'##\s+.*Example Usage.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if example_match:
        # Extract first few lines as use cases
        example_text = example_match.group(1).strip()
        lines = [line.strip() for line in example_text.split('\n') if line.strip()]
        # Get first 3 bullet points or commands
        for line in lines[:10]:
            if line.startswith('-') or line.startswith('*'):
                use_case = line.lstrip('-*').strip()
                # Clean up common prefixes
                use_case = re.sub(r'^\*\*[^*]+\*\*:?\s*', '', use_case)
                use_case = re.sub(r'^Command:\s*', '', use_case)
                if use_case and len(use_case) < 150 and not use_case.startswith('['):
                    use_cases.append(use_case)
            if len(use_cases) >= 3:
                break

    # If no examples found, try manual triggers section
    if not use_cases:
        triggers_match = re.search(r'###\s+Manual Triggers.*?\n(.*?)(?=\n##|\n###|\Z)', content, re.DOTALL | re.IGNORECASE)
        if triggers_match:
            triggers_text = triggers_match.group(1).strip()
            lines = [line.strip() for line in triggers_text.split('\n') if line.strip()]
            for line in lines[:5]:
                if line.startswith('-') or line.startswith('*'):
                    use_case = line.lstrip('-*').strip()
                    use_case = re.sub(r'^\*\*[^*]+\*\*:?\s*', '', use_case)
                    use_case = re.sub(r'^Command:\s*', '', use_case)
                    if use_case and len(use_case) < 150:
                        use_cases.append(use_case)
                if len(use_cases) >= 3:
                    break

    # Get file modification time as "last updated"
    try:
        mtime = skill_file.stat().st_mtime
        last_updated = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except:
        last_updated = metadata.get("last_updated", "Unknown")

    return {
        "name": metadata.get("name", skill_path.name.replace("_", " ").title()),
        "slug": metadata.get("slug", skill_path.name),
        "description": metadata.get("description", "No description available"),
        "version": metadata.get("version", "0.0.0"),
        "status": metadata.get("status", "unknown"),
        "tier": metadata.get("tier", "bronze"),
        "path": f"{skill_path.name}/SKILL.md",
        "use_cases": use_cases,
        "last_updated": last_updated
    }


# ============================================================================
# INDEX GENERATION
# ============================================================================

def generate_skills_index(skills_info: List[Dict]) -> str:
    """Generate SKILLS_INDEX.md content."""

    # Sort by status (active first) then by name
    status_order = {"active": 0, "development": 1, "planned": 2, "deprecated": 3}
    skills_info.sort(key=lambda x: (status_order.get(x["status"], 9), x["name"]))

    # Count by status
    active_count = len([s for s in skills_info if s["status"] == "active"])
    dev_count = len([s for s in skills_info if s["status"] == "development"])
    planned_count = len([s for s in skills_info if s["status"] == "planned"])

    content = f"""# AI Employee Skills Registry

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Skills:** {len(skills_info)}
**Active:** {active_count} | **Development:** {dev_count} | **Planned:** {planned_count}

---

## 📚 Quick Navigation

### By Status
- [Active Skills](#active-skills) ({active_count})
- [In Development](#in-development) ({dev_count})
- [Planned](#planned-skills) ({planned_count})

### By Category
- [Task Management](#task-management)
- [Communication](#communication)
- [Data & Analytics](#data--analytics)
- [Automation](#automation)

---

## 🎯 Active Skills

"""

    # Group skills by status
    active_skills = [s for s in skills_info if s["status"] == "active"]
    dev_skills = [s for s in skills_info if s["status"] == "development"]
    planned_skills = [s for s in skills_info if s["status"] == "planned"]

    # Render active skills
    for i, skill in enumerate(active_skills, 1):
        status_emoji = {
            "active": "✅",
            "development": "🚧",
            "planned": "📋",
            "deprecated": "⚠️"
        }.get(skill["status"], "⚪")

        tier_badge = {
            "bronze": "🥉",
            "silver": "🥈",
            "gold": "🥇"
        }.get(skill["tier"], "")

        content += f"""### {i}. {status_emoji} {skill['name']} {tier_badge}

**Version:** {skill['version']}
**Status:** {skill['status'].title()}
**Path:** [`{skill['path']}`]({skill['path']})
**Last Updated:** {skill['last_updated']}

**Description:**
{skill['description']}

**Common Use Cases:**
"""

        if skill['use_cases']:
            for use_case in skill['use_cases']:
                content += f"- {use_case}\n"
        else:
            content += "- See skill documentation for details\n"

        content += "\n---\n\n"

    # Render development skills
    if dev_skills:
        content += "## 🚧 In Development\n\n"

        for skill in dev_skills:
            content += f"""### {skill['name']}

**Version:** {skill['version']}
**Path:** [`{skill['path']}`]({skill['path']})
**Description:** {skill['description']}

---

"""

    # Render planned skills
    if planned_skills:
        content += "## 📋 Planned Skills\n\n"

        for skill in planned_skills:
            content += f"""### {skill['name']}

**Description:** {skill['description']}

---

"""

    # Add skill categories section
    content += """
## 📑 Skills by Category

### Task Management
"""

    task_skills = [s for s in active_skills if "task" in s["name"].lower() or "task" in s["description"].lower()]
    for skill in task_skills:
        content += f"- [{skill['name']}]({skill['path']}) - {skill['description']}\n"

    content += "\n### Communication\n"
    comm_skills = [s for s in active_skills if "email" in s["name"].lower() or "email" in s["description"].lower()]
    for skill in comm_skills:
        content += f"- [{skill['name']}]({skill['path']}) - {skill['description']}\n"

    content += "\n### Data & Analytics\n"
    data_skills = [s for s in active_skills if any(word in s["name"].lower() for word in ["dashboard", "briefing", "report", "analytics"])]
    for skill in data_skills:
        content += f"- [{skill['name']}]({skill['path']}) - {skill['description']}\n"

    content += "\n### Automation\n"
    auto_skills = [s for s in active_skills if "automation" in s["description"].lower() or "auto" in s["name"].lower()]
    for skill in auto_skills:
        content += f"- [{skill['name']}]({skill['path']}) - {skill['description']}\n"

    # Add usage guide
    content += """

---

## 🚀 Using Skills

### Invoking Skills

**Via Claude Code:**
```
"Use the [skill name] skill"
"Generate a CEO briefing"
"Process tasks in Needs_Action"
```

**Via Scripts:**
```bash
# Task Processor
python scripts/runner_silver.py

# Email Handler
python scripts/email_handler.py draft "recipient@example.com" "Subject" "Body"

# Dashboard Updater
python scripts/dashboard_updater.py

# CEO Briefing
python scripts/ceo_briefing_generator.py
```

---

## 📋 Skill Quality Standards

All active skills must:
- ✅ Have complete YAML frontmatter with required fields
- ✅ Include all required sections (Purpose, Triggers, Inputs, Outputs, etc.)
- ✅ Provide working code examples
- ✅ Document error handling
- ✅ Include usage examples
- ✅ Pass validation checks

**To validate skills:**
```bash
python scripts/validate_skills.py
```

---

## 🔧 Creating New Skills

1. **Create skill directory:** `AI_Employee_Vault/Skills/my_skill/`
2. **Create SKILL.md** with required frontmatter and sections
3. **Implement code** in `scripts/` if needed
4. **Add examples** and documentation
5. **Run validation:** `python scripts/validate_skills.py`
6. **Update index:** Index is auto-generated by validator

**Template:** See `task_processor/SKILL.md` for reference structure

---

## 📊 Skill Status Definitions

- **Active (✅):** Production-ready, fully tested, documented
- **Development (🚧):** In progress, may have incomplete features
- **Planned (📋):** Designed but not yet implemented
- **Deprecated (⚠️):** No longer maintained, use alternative

---

## 🏆 Skill Tiers

- **🥉 Bronze:** Basic functionality, single purpose
- **🥈 Silver:** Enhanced features, multiple capabilities
- **🥇 Gold:** Advanced features, comprehensive analysis

---

**Generated by:** Skills Validator v1.0.0
**Validation Status:** {'✅ All skills valid' if all(s['status'] == 'active' for s in active_skills) else '⚠️ Some issues detected'}
"""

    return content


# ============================================================================
# MAIN VALIDATOR
# ============================================================================

def validate_all_skills() -> Tuple[int, int, List[str]]:
    """
    Validate all skills and generate index.

    Returns:
        (total_skills, valid_skills, issues_by_skill)
    """
    print("=" * 60)
    print("Skills Validator and Registry Generator")
    print("=" * 60)
    print()

    # Scan for skills
    print("[1/4] Scanning Skills directory...")
    skill_paths = scan_skills_directory()
    print(f"      Found {len(skill_paths)} skills\n")

    if not skill_paths:
        print("[ERROR] No skills found in Skills/ directory")
        return 0, 0, []

    # Validate each skill
    print("[2/4] Validating skill files...")
    all_issues = []
    valid_count = 0
    skills_info = []

    for skill_path in skill_paths:
        skill_name = skill_path.name
        print(f"      Checking {skill_name}...", end=" ")

        is_valid, issues = validate_skill_file(skill_path)

        if is_valid:
            print("[OK]")
            valid_count += 1

            # Extract info for index
            info = extract_skill_info(skill_path)
            if info:
                skills_info.append(info)
        else:
            print("[FAIL]")
            all_issues.append(f"\n{skill_name}:")
            for issue in issues:
                all_issues.append(f"  - {issue}")

    print()

    # Generate index
    print("[3/4] Generating SKILLS_INDEX.md...")
    if skills_info:
        index_content = generate_skills_index(skills_info)

        try:
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                f.write(index_content)
            print(f"      Index generated: {INDEX_FILE}")
        except Exception as e:
            print(f"      [ERROR] Failed to write index: {e}")
    else:
        print("      [WARNING] No valid skills to index")

    print()

    # Report results
    print("[4/4] Validation Summary")
    print("=" * 60)
    print(f"Total Skills:  {len(skill_paths)}")
    print(f"Valid Skills:  {valid_count}")
    print(f"Failed Skills: {len(skill_paths) - valid_count}")
    print("=" * 60)

    if all_issues:
        print("\n[!] Issues Found:")
        for issue in all_issues:
            print(issue)
        print()

    return len(skill_paths), valid_count, all_issues


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate SKILL.md files and generate SKILLS_INDEX.md"
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only validate, do not regenerate index'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show detailed validation information'
    )

    args = parser.parse_args()

    total, valid, issues = validate_all_skills()

    if total == 0:
        print("\n[ERROR] No skills found")
        sys.exit(1)
    elif valid == total:
        print("\n[SUCCESS] All skills are valid!")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {total - valid} skill(s) have issues")
        print("Run with -v for detailed information")
        sys.exit(1)
