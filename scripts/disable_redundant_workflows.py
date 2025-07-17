#!/usr/bin/env python3
"""
Disable redundant GitHub Actions workflows to reduce CI noise
Per CTO directive to consolidate from 64 checks to ~10-15
"""

import shutil
from pathlib import Path

# Workflows to disable (move to .disabled extension)
WORKFLOWS_TO_DISABLE = [
    # Keep tests.yml but we'll modify it to run only Python 3.11
    "test-orchestration.yml",      # Redundant with consolidated-ci
    "qa_validation.yml",           # Redundant with consolidated-ci  
    "quality-gate.yml",            # Redundant with consolidated-ci
    "visual-qa-validation.yml",    # Too noisy
    "pr-validation.yml",           # Redundant with consolidated-ci
    "agent-pr-validation.yml",     # Too specific
    "autonomous-pr-handler.yml",   # Keep orchestrator but reduce its triggers
    "ai-suggestions-processor.yml", # Too noisy
    "autonomous-coderabbit-handler.yml", # CodeRabbit is now configured via .coderabbit.yml
    "intelligent-pr-fixer.yml",    # Too many automated fixes
    "intelligent-conflict-resolver.yml", # Keep but make manual trigger only
    "requirements-health-check.yml", # Can be part of consolidated-ci
]

# Workflows to modify (reduce triggers)
WORKFLOWS_TO_MODIFY = {
    "tests.yml": {
        "change": "Remove Python 3.12 from matrix to reduce duplicate checks",
        "action": "modify_matrix"
    },
    "sonarcloud.yml": {
        "change": "Run only on main branch pushes, not PRs",
        "action": "modify_triggers"
    },
    "worktree-orchestration.yml": {
        "change": "Reduce frequency of scheduled runs",
        "action": "modify_schedule"
    }
}

def disable_workflow(workflow_path: Path):
    """Disable a workflow by renaming it"""
    disabled_path = workflow_path.with_suffix('.yml.disabled')
    
    if workflow_path.exists():
        shutil.move(str(workflow_path), str(disabled_path))
        print(f"✅ Disabled: {workflow_path.name} -> {disabled_path.name}")
    else:
        print(f"⚠️  Not found: {workflow_path.name}")

def modify_tests_workflow(workflow_path: Path):
    """Modify tests.yml to only run Python 3.11"""
    if not workflow_path.exists():
        return
        
    content = workflow_path.read_text()
    
    # Replace the matrix to only include Python 3.11
    new_content = content.replace(
        "python-version: ['3.11', '3.12']",
        "python-version: ['3.11']"
    )
    
    workflow_path.write_text(new_content)
    print(f"✅ Modified {workflow_path.name}: Removed Python 3.12 from matrix")

def modify_sonarcloud_workflow(workflow_path: Path):
    """Modify SonarCloud to run only on main pushes"""
    if not workflow_path.exists():
        return
        
    content = workflow_path.read_text()
    
    # Remove pull_request trigger
    lines = content.split('\n')
    new_lines = []
    skip_pr_section = False
    
    for line in lines:
        if 'pull_request:' in line and not line.strip().startswith('#'):
            skip_pr_section = True
        elif skip_pr_section and line.strip() and not line.startswith(' '):
            skip_pr_section = False
            
        if not skip_pr_section:
            new_lines.append(line)
    
    workflow_path.write_text('\n'.join(new_lines))
    print(f"✅ Modified {workflow_path.name}: Removed PR triggers")

def main():
    """Main function to clean up workflows"""
    workflows_dir = Path(__file__).parent.parent / ".github" / "workflows"
    
    print("🧹 Cleaning up redundant workflows...")
    print(f"📁 Workflows directory: {workflows_dir}")
    
    # Count current workflows
    current_count = len(list(workflows_dir.glob("*.yml")))
    print(f"📊 Current workflow count: {current_count}")
    
    # Disable redundant workflows
    print("\n🚫 Disabling redundant workflows...")
    for workflow_name in WORKFLOWS_TO_DISABLE:
        workflow_path = workflows_dir / workflow_name
        disable_workflow(workflow_path)
    
    # Modify workflows
    print("\n✏️  Modifying workflows to reduce noise...")
    
    # Modify tests.yml
    tests_path = workflows_dir / "tests.yml"
    modify_tests_workflow(tests_path)
    
    # Modify sonarcloud.yml  
    sonar_path = workflows_dir / "sonarcloud.yml"
    modify_sonarcloud_workflow(sonar_path)
    
    # Count remaining active workflows
    remaining_count = len(list(workflows_dir.glob("*.yml")))
    print(f"\n📊 Remaining active workflows: {remaining_count}")
    print(f"🎯 Reduced by: {current_count - remaining_count} workflows")
    
    print("\n✅ Workflow cleanup complete!")
    print("\n📝 Next steps:")
    print("1. Review .github/workflows/consolidated-ci.yml")
    print("2. Ensure critical checks are not missing")
    print("3. Monitor PR #130 to see reduced bot noise")

if __name__ == "__main__":
    main()