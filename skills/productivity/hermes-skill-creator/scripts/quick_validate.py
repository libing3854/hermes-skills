#!/usr/bin/env python3
"""
Quick validation script for skills — Hermes Agent adapted version.

Validates a skill's SKILL.md structure without Claude-specific validation rules.
Checks: frontmatter format, required fields, naming conventions, field length limits.

Usage:
    python quick_validate.py <skill_directory>
    
Example:
    python quick_validate.py ~/.hermes/skills/productivity/hermes-skill-creator/
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


def validate_skill(skill_path):
    """Full validation of a skill's SKILL.md using PyYAML parser."""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read content
    content = skill_md.read_text()
    
    # Check frontmatter start
    if not content.startswith('---'):
        return False, "No YAML frontmatter found — file must start with '---'"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format — must be '---\\n...\\n---'"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter with proper YAML parser
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties for Hermes Agent skills
    ALLOWED_PROPERTIES = {'name', 'description', 'version', 'author', 'license', 'metadata', 'allowed-tools', 'compatibility'}

    # Check for unexpected top-level keys
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Validate name
    name = frontmatter.get('name', '')
    if not isinstance(name, str) or not name.strip():
        return False, "Name must be a non-empty string"
    name = name.strip()
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, hyphens only)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str) or not description.strip():
        return False, "Description must be a non-empty string"
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate compatibility field if present
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    # Check total file size
    if len(content) > 100_000:
        return False, f"SKILL.md is too large ({len(content)} characters). Maximum is 100,000 characters."

    return True, f"Skill '{name}' is valid! Description: {len(description)} chars, Total: {len(content)} chars"


def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    if not Path(skill_path).exists():
        print(f"❌ Error: Directory not found: {skill_path}")
        sys.exit(1)

    valid, message = validate_skill(skill_path)
    if valid:
        print(f"✅ {message}")
        sys.exit(0)
    else:
        print(f"❌ Validation failed: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
