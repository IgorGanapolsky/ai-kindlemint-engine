#!/usr/bin/env python3
"""
Generate Claude Cost Badge for GitHub Repository
Creates a shields.io badge showing current Claude API costs
"""

import json
from pathlib import Path
from urllib.parse import quote


def generate_cost_badge():
    """Generate cost badge data for GitHub README"""
    
    # Load current cost data
    repo_root = Path(__file__).parent.parent
    commit_costs_file = repo_root / "commit_costs.json"
    
    if not commit_costs_file.exists():
        return {
            "badge_url": "https://img.shields.io/badge/Claude%20Cost-Not%20Tracked-red",
            "cost": "Not Tracked",
            "total_cost": 0.0
        }
    
    try:
        with open(commit_costs_file, 'r') as f:
            cost_data = json.load(f)
        
        total_cost = cost_data.get('total_cost', 0.0)
        last_commit = cost_data.get('commits', [])[-1] if cost_data.get('commits') else None
        
        # Format costs for badge
        if total_cost < 0.01:
            cost_label = f"${total_cost:.6f}"
        elif total_cost < 1.0:
            cost_label = f"${total_cost:.4f}"
        else:
            cost_label = f"${total_cost:.2f}"
        
        # Choose color based on cost
        if total_cost < 0.50:
            color = "green"
        elif total_cost < 2.00:
            color = "yellow"
        else:
            color = "orange"
        
        # Generate shields.io badge URL
        badge_text = f"Claude Cost-{cost_label}-{color}"
        badge_url = f"https://img.shields.io/badge/{quote(badge_text)}"
        
        return {
            "badge_url": badge_url,
            "cost": cost_label,
            "total_cost": total_cost,
            "commits": len(cost_data.get('commits', [])),
            "last_commit_cost": last_commit.get('cost', 0.0) if last_commit else 0.0
        }
        
    except Exception as e:
        return {
            "badge_url": "https://img.shields.io/badge/Claude%20Cost-Error-red",
            "cost": "Error",
            "total_cost": 0.0,
            "error": str(e)
        }


def update_readme_badge():
    """Update README.md with current cost badge"""
    repo_root = Path(__file__).parent.parent
    readme_file = repo_root / "README.md"
    
    if not readme_file.exists():
        print("❌ README.md not found")
        return False
    
    badge_data = generate_cost_badge()
    
    # Read current README
    with open(readme_file, 'r') as f:
        content = f.read()
    
    # Look for existing Claude cost badge
    import re
    
    # Pattern to match Claude cost badge
    badge_pattern = r'!\[Claude Cost\]\(https://img\.shields\.io/badge/Claude%20Cost-[^)]+\)'
    new_badge = f"![Claude Cost]({badge_data['badge_url']})"
    
    if re.search(badge_pattern, content):
        # Replace existing badge
        content = re.sub(badge_pattern, new_badge, content)
        print(f"✅ Updated existing Claude cost badge: {badge_data['cost']}")
    else:
        # Add new badge after first line (title)
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            # Find the badge section or create one
            badge_line = None
            for i, line in enumerate(lines):
                if 'img.shields.io' in line or line.strip().startswith('!['):
                    badge_line = i
                    break
            
            if badge_line is not None:
                # Insert after existing badges
                lines.insert(badge_line + 1, new_badge)
            else:
                # Insert after title
                lines.insert(2, new_badge)
                lines.insert(2, '')  # Empty line before badge
            
            content = '\n'.join(lines)
            print(f"✅ Added new Claude cost badge: {badge_data['cost']}")
    
    # Write updated README
    with open(readme_file, 'w') as f:
        f.write(content)
    
    return True


if __name__ == "__main__":
    print("🔄 Generating Claude Cost Badge...")
    
    badge_data = generate_cost_badge()
    print(f"📊 Total Claude Cost: {badge_data['cost']}")
    print(f"🔗 Badge URL: {badge_data['badge_url']}")
    
    if update_readme_badge():
        print("✅ README.md updated with cost badge")
    else:
        print("❌ Failed to update README.md")