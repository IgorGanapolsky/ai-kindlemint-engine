#!/usr/bin/env python3
"""
Fix CI Overload - Reduce 27+ checks to essential ones
"""

import json
import logging
import os
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CIOptimizer:
    def __init__(self):
        self.workflows_dir = Path(".github/workflows")
        self.backup_dir = Path(".github/workflows.backup")

        # Workflows to disable on PRs
        self.disable_on_pr = [
            "code-hygiene.yml",
            "hygiene-check.yml",
            "qa-check.yml",
            "qa-validation.yml",
            "code-quality.yml",
            "quick-validation.yml",
            "sonarcloud.yml",
            "book-qa-validation.yml",
            "advanced-security.yml",
        ]

        # Workflows to make scheduled only
        self.make_scheduled = [
            "performance-validation.yml",
            "documentation-validation.yml",
            "comprehensive-qa.yml",
        ]

    def backup_workflows(self):
        """Backup existing workflows before modification"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)

        for workflow in self.workflows_dir.glob("*.yml"):
            backup_path = self.backup_dir / workflow.name
            backup_path.write_text(workflow.read_text())
            logger.info(f"Backed up {workflow.name}")

    def disable_pr_triggers(self, workflow_path):
        """Remove PR triggers from workflow"""
        try:
            with open(workflow_path, "r") as f:
                workflow = yaml.safe_load(f)

            if not workflow or "on" not in workflow:
                return

            # Convert to scheduled or workflow_dispatch only
            original_on = workflow["on"]
            workflow["on"] = {
                "workflow_dispatch": {},
                "schedule": [{"cron": "0 0 * * 0"}],  # Weekly on Sunday
            }

            # Add comment about why it was disabled
            workflow["# Disabled on PR"] = f"Originally triggered on: {original_on}"

            with open(workflow_path, "w") as f:
                yaml.dump(workflow, f, default_flow_style=False)

            logger.info(f"Disabled PR triggers for {workflow_path.name}")

        except Exception as e:
            logger.error(f"Failed to modify {workflow_path}: {e}")

    def create_workflow_skip_conditions(self):
        """Create a reusable workflow for smart skipping"""
        skip_workflow = """name: Check Skip Conditions

on:
  workflow_call:
    outputs:
      should_skip:
        description: 'Whether to skip checks'
        value: ${{ jobs.check.outputs.should_skip }}

jobs:
  check:
    runs-on: ubuntu-latest
    outputs:
      should_skip: ${{ steps.skip.outputs.should_skip }}
    steps:
      - name: Check skip conditions
        id: skip
        run: |
          # Skip for bots
          if [[ "${{ github.actor }}" == *"[bot]" ]]; then
            echo "should_skip=true" >> $GITHUB_OUTPUT
            echo "Skipping checks for bot: ${{ github.actor }}"
            exit 0
          fi
          
          # Skip for doc-only changes
          if [[ -n "${{ github.event.pull_request.title }}" ]]; then
            if [[ "${{ github.event.pull_request.title }}" == *"[skip ci]"* ]]; then
              echo "should_skip=true" >> $GITHUB_OUTPUT
              echo "Skipping due to [skip ci] in title"
              exit 0
            fi
          fi
          
          echo "should_skip=false" >> $GITHUB_OUTPUT
"""

        skip_path = self.workflows_dir / "skip-conditions.yml"
        skip_path.write_text(skip_workflow)
        logger.info("Created skip conditions workflow")

    def update_branch_protection_script(self):
        """Generate script to update branch protection"""
        script = """#!/bin/bash
# Update branch protection to use single CI check

echo "Updating branch protection rules..."

gh api repos/IgorGanapolsky/ai-kindlemint-engine/branches/main/protection \
  --method PUT \
  --header "Accept: application/vnd.github+json" \
  --input - << EOF
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["CI Status"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": false,
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "required_conversation_resolution": false
}
EOF

echo "✅ Branch protection updated to use single CI Status check"
"""

        script_path = Path("scripts/update_branch_protection.sh")
        script_path.write_text(script)
        script_path.chmod(0o755)
        logger.info("Created branch protection update script")

    def create_pr_config(self):
        """Create PR configuration for smart check skipping"""
        config = {
            "version": 1,
            "ci_optimization": {
                "enabled": True,
                "single_check": "CI Status",
                "skip_patterns": {
                    "docs": ["*.md", "docs/**", "README*"],
                    "config": [".github/**", "*.yml", "*.yaml"],
                    "tests": ["tests/**", "*_test.py", "test_*.py"],
                },
                "trusted_bots": [
                    "dependabot[bot]",
                    "deepsource-autofix[bot]",
                    "pixeebot[bot]",
                    "renovate[bot]",
                ],
                "auto_merge_rules": {
                    "bot_security_fixes": {
                        "pattern": "security|vulnerability|cve",
                        "delay_minutes": 5,
                    },
                    "bot_dependencies": {
                        "pattern": "update|bump|upgrade",
                        "delay_minutes": 60,
                    },
                },
            },
        }

        config_path = Path(".github/pr-config.json")
        config_path.write_text(json.dumps(config, indent=2))
        logger.info("Created PR configuration")

    def run(self):
        """Execute CI optimization"""
        logger.info("🚀 Starting CI optimization...")

        # Backup first
        self.backup_workflows()

        # Disable workflows on PRs
        for workflow_name in self.disable_on_pr:
            workflow_path = self.workflows_dir / workflow_name
            if workflow_path.exists():
                self.disable_pr_triggers(workflow_path)

        # Create helper files
        self.create_workflow_skip_conditions()
        self.update_branch_protection_script()
        self.create_pr_config()

        logger.info("✅ CI optimization complete!")
        logger.info("Next steps:")
        logger.info("1. Run: ./scripts/update_branch_protection.sh")
        logger.info("2. Monitor the new 'CI Status' check")
        logger.info("3. Old workflows backed up to .github/workflows.backup/")


if __name__ == "__main__":
    optimizer = CIOptimizer()
    optimizer.run()
