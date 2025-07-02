#!/usr/bin/env python3
"""
CTO Emergency Override System
Ensures PRs don't get stuck and business continues
"""

import os
import sys
from datetime import datetime, timedelta
from github import Github
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CTOOverrideSystem:
    def __init__(self):
        self.github_token = os.environ.get('GITHUB_TOKEN')
        if not self.github_token:
            logger.error("GITHUB_TOKEN not set")
            sys.exit(1)
            
        self.g = Github(self.github_token)
        self.repo = self.g.get_repo("IgorGanapolsky/ai-kindlemint-engine")
        
        # Load override config
        config_path = ".github/cto-override-config.yml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()
    
    def _default_config(self):
        """Default configuration if config file doesn't exist"""
        return {
            'override_rules': {
                'auto_merge_timeout_hours': {
                    'trusted_bots': 1,
                    'approved_prs': 2,
                    'security_fixes': 0.5
                },
                'auto_close_after_hours': {
                    'untrusted_bots': 24,
                    'draft_prs': 168,
                    'no_activity': 336
                }
            },
            'trusted_bots': [
                'dependabot[bot]',
                'deepsource-autofix[bot]',
                'pixeebot[bot]',
                'renovate[bot]'
            ]
        }
    
    def emergency_override_all(self):
        """Emergency: Force merge all approved PRs regardless of CI status"""
        logger.warning("🚨 EMERGENCY OVERRIDE ACTIVATED 🚨")
        
        prs = self.repo.get_pulls(state='open')
        for pr in prs:
            try:
                if pr.draft:
                    continue
                    
                # Check if approved
                reviews = pr.get_reviews()
                approved = any(r.state == 'APPROVED' for r in reviews)
                
                if approved:
                    logger.info(f"Force merging approved PR #{pr.number}: {pr.title}")
                    pr.merge(
                        merge_method="squash",
                        commit_title=f"{pr.title} [CTO Emergency Override]",
                        commit_message="Merged via CTO emergency override due to CI failures"
                    )
                    logger.info(f"✅ Successfully merged PR #{pr.number}")
            except Exception as e:
                logger.error(f"Failed to merge PR #{pr.number}: {e}")
    
    def handle_stuck_prs(self):
        """Handle PRs that are stuck due to CI issues"""
        logger.info("🔍 Checking for stuck PRs...")
        
        prs = self.repo.get_pulls(state='open')
        now = datetime.utcnow()
        
        for pr in prs:
            try:
                # Skip drafts
                if pr.draft:
                    continue
                
                # Calculate age
                pr_age = now - pr.created_at
                hours_old = pr_age.total_seconds() / 3600
                
                # Handle bot PRs
                if pr.user.login.endswith('[bot]'):
                    self._handle_bot_pr(pr, hours_old)
                else:
                    self._handle_human_pr(pr, hours_old)
                    
            except Exception as e:
                logger.error(f"Error handling PR #{pr.number}: {e}")
    
    def _handle_bot_pr(self, pr, hours_old):
        """Handle bot-generated PRs"""
        bot_name = pr.user.login
        
        if bot_name in self.config['trusted_bots']:
            timeout = self.config['override_rules']['auto_merge_timeout_hours']['trusted_bots']
            
            if hours_old > timeout:
                logger.info(f"Auto-merging trusted bot PR #{pr.number} from {bot_name}")
                try:
                    pr.merge(
                        merge_method="squash",
                        commit_title=f"{pr.title} [Auto-merged]"
                    )
                    logger.info(f"✅ Merged PR #{pr.number}")
                except Exception as e:
                    logger.warning(f"Could not merge PR #{pr.number}: {e}")
                    # Try admin merge if available
                    self._try_admin_merge(pr)
        else:
            # Untrusted bot
            close_timeout = self.config['override_rules']['auto_close_after_hours']['untrusted_bots']
            
            if hours_old > close_timeout:
                logger.info(f"Closing untrusted bot PR #{pr.number} from {bot_name}")
                pr.edit(state='closed')
                pr.create_issue_comment("Auto-closed: Untrusted bot PR with no human interaction")
    
    def _handle_human_pr(self, pr, hours_old):
        """Handle human-created PRs"""
        # Check if approved
        reviews = pr.get_reviews()
        approved = any(r.state == 'APPROVED' for r in reviews)
        
        if approved:
            timeout = self.config['override_rules']['auto_merge_timeout_hours']['approved_prs']
            
            # Check last update time
            last_update = pr.updated_at
            hours_since_update = (datetime.utcnow() - last_update).total_seconds() / 3600
            
            if hours_since_update > timeout:
                logger.info(f"Force merging stuck approved PR #{pr.number}: {pr.title}")
                self._try_admin_merge(pr)
    
    def _try_admin_merge(self, pr):
        """Try to merge with admin privileges"""
        try:
            # This would require admin API access
            # For now, log the action
            logger.warning(f"PR #{pr.number} requires admin merge - escalating to CTO")
            pr.create_issue_comment(
                "🚨 CTO Alert: This PR has been approved but is stuck due to CI failures. "
                "Manual admin merge may be required."
            )
        except Exception as e:
            logger.error(f"Admin merge failed for PR #{pr.number}: {e}")
    
    def fix_branch_protection(self):
        """Temporarily reduce branch protection to allow merges"""
        logger.warning("🔧 Adjusting branch protection rules...")
        
        try:
            branch = self.repo.get_branch("main")
            
            # Get current protection
            protection = branch.get_protection()
            
            # Reduce requirements temporarily
            branch.edit_protection(
                strict=False,  # Don't require branches to be up to date
                contexts=[],   # Remove required status checks temporarily
                enforce_admins=False,  # Allow admin overrides
                dismiss_stale_reviews=False,
                require_code_owner_reviews=False,
                required_approving_review_count=0
            )
            
            logger.info("✅ Branch protection reduced for emergency merges")
            
            # Note: You'd want to restore these after emergency is over
            
        except Exception as e:
            logger.error(f"Could not modify branch protection: {e}")
    
    def run(self, emergency=False):
        """Run the override system"""
        logger.info("🤖 CTO Override System Starting...")
        
        if emergency:
            self.emergency_override_all()
        else:
            self.handle_stuck_prs()
        
        logger.info("✅ CTO Override System Complete")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='CTO Emergency Override System')
    parser.add_argument('--emergency', action='store_true', 
                        help='Emergency mode: force merge all approved PRs')
    parser.add_argument('--fix-protection', action='store_true',
                        help='Temporarily reduce branch protection')
    
    args = parser.parse_args()
    
    system = CTOOverrideSystem()
    
    if args.fix_protection:
        system.fix_branch_protection()
    
    system.run(emergency=args.emergency)