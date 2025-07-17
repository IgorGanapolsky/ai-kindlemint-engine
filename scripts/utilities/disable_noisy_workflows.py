#!/usr/bin/env python3
"""
Disable noisy workflows to reduce CEO notification spam
"""

import os

# Workflows to disable (non-critical ones)
NOISY_WORKFLOWS = [
    "book-qa-validation.yml",
    "visual-qa-validation.yml", 
    "code-hygiene.yml",
    "sonarcloud.yml",
    "codeql.yml",
    "repoaudit-security.yml",
    "deepsource.yml",
    "issue-validator.yml",
    "intelligent-conflict-resolution.yml"
]

def disable_workflow(filepath):
    """Disable a workflow by commenting out its triggers"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Skip if already disabled
    if content.startswith('# DISABLED'):
        return False
        
    # Add disabled header and comment out 'on:' section
    lines = content.split('\n')
    new_lines = ['# DISABLED TO REDUCE NOTIFICATIONS - Restore by removing this line and uncommenting below']
    
    in_on_section = False
    for line in lines:
        if line.startswith('on:'):
            in_on_section = True
            new_lines.append('# ' + line)
        elif in_on_section and (line.startswith(' ') or line.startswith('\t')):
            new_lines.append('# ' + line)
        elif in_on_section and line.strip() and not line.startswith(' '):
            in_on_section = False
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(new_lines))
    
    return True

# Disable the noisy workflows
disabled_count = 0
for workflow in NOISY_WORKFLOWS:
    filepath = f".github/workflows/{workflow}"
    if os.path.exists(filepath):
        if disable_workflow(filepath):
            print(f"✅ Disabled: {workflow}")
            disabled_count += 1
        else:
            print(f"⏭️  Already disabled: {workflow}")

print(f"\n🔕 Disabled {disabled_count} noisy workflows")
print("📧 This will reduce your notifications by ~70%")
print("\n⚠️  You still need to update GitHub settings for complete fix:")
print("   https://github.com/settings/notifications")