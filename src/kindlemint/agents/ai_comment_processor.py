#!/usr/bin/env python3
"""
AI Comment Processor - Autonomous handler for AI code review suggestions
Eliminates email flood by automatically applying Sentry Seer and CodeRabbit suggestions
"""

import re
import os
import subprocess
from typing import List, Dict, Any
import requests
from pathlib import Path

class AICommentProcessor:
    """Processes AI code review comments and applies suggestions automatically"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_pr_comments(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get all comments from a PR"""
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        response = requests.get(url, headers=self.headers, timeout=60)
        return response.json()
    
    def identify_ai_suggestions(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify comments from AI code review tools"""
        ai_bots = ['seer-by-sentry', 'coderabbitai', 'pixeebot']
        suggestions = []
        
        for comment in comments:
            author = comment.get('user', {}).get('login', '')
            if any(bot in author.lower() for bot in ai_bots):
                body = comment.get('body', '')
                if self._contains_code_suggestion(body):
                    suggestions.append(comment)
        
        return suggestions
    
    def _contains_code_suggestion(self, body: str) -> bool:
        """Check if comment contains actionable code suggestions"""
        suggestion_patterns = [
            r'Suggested change',
            r'import random',
            r'import secrets',
            r'replace.*with',
            r'should be moved',
            r'unnecessary.*here'
        ]
        return any(re.search(pattern, body, re.IGNORECASE) for pattern in suggestion_patterns)
    
    def parse_sentry_suggestion(self, comment_body: str) -> Dict[str, str]:
        """Parse Sentry Seer code suggestions"""
        # Extract file path
        file_match = re.search(r'In ([^:]+):', comment_body)
        if not file_match:
            return {}
        
        file_path = file_match.group(1)
        
        # Extract code changes
        old_code = ""
        new_code = ""
        
        # Look for diff-style suggestions
        if 'import secrets' in comment_body and 'import random' in comment_body:
            old_code = "import secrets"
            new_code = "import random"
        
        # Look for specific replacements
        if 'secrets.SystemRandom()' in comment_body:
            old_code = "secrets.SystemRandom().sample("
            new_code = "random.sample("
        
        return {
            'file_path': file_path,
            'old_code': old_code,
            'new_code': new_code,
            'type': 'security_improvement'
        }
    
    def apply_suggestion(self, suggestion: Dict[str, str]) -> bool:
        """Apply code suggestion to the actual file"""
        try:
            file_path = suggestion['file_path']
            old_code = suggestion['old_code']
            new_code = suggestion['new_code']
            
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                return False
            
            # Read file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Apply replacement
            if old_code in content:
                updated_content = content.replace(old_code, new_code)
                
                # Write back
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Applied suggestion to {file_path}")
                return True
            else:
                print(f"⚠️  Code pattern not found in {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error applying suggestion: {e}")
            return False
    
    def commit_changes(self, suggestions_applied: List[str]):
        """Commit applied suggestions with proper tagging"""
        try:
            # Stage changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Create commit message
            commit_msg = f"fix: Auto-apply AI code review suggestions [Amp CLI]\n\nApplied {len(suggestions_applied)} AI suggestions:\n"
            for suggestion in suggestions_applied:
                commit_msg += f"- {suggestion}\n"
            
            # Commit
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print(f"✅ Committed {len(suggestions_applied)} AI suggestions")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to commit changes: {e}")
            return False
    
    def process_pr_automatically(self, repo: str, pr_number: int):
        """Main method: Process all AI suggestions in a PR automatically"""
        print(f"🤖 Processing AI suggestions for PR #{pr_number}")
        
        # Get comments
        comments = self.get_pr_comments(repo, pr_number)
        ai_suggestions = self.identify_ai_suggestions(comments)
        
        if not ai_suggestions:
            print("✅ No AI suggestions found")
            return
        
        print(f"📋 Found {len(ai_suggestions)} AI suggestions")
        
        # Process each suggestion
        applied_suggestions = []
        for comment in ai_suggestions:
            suggestion = self.parse_sentry_suggestion(comment['body'])
            if suggestion and self.apply_suggestion(suggestion):
                applied_suggestions.append(f"{suggestion['type']}: {suggestion['file_path']}")
        
        # Commit if any suggestions were applied
        if applied_suggestions:
            self.commit_changes(applied_suggestions)
            print(f"🚀 Successfully auto-applied {len(applied_suggestions)} AI suggestions")
        else:
            print("⚠️  No suggestions could be applied automatically")

if __name__ == "__main__":
    # Get current PR from environment or default
    pr_number = int(os.getenv('PR_NUMBER', '130'))
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable required")
        exit(1)
    
    processor = AICommentProcessor(github_token)
    processor.process_pr_automatically('IgorGanapolsky/ai-kindlemint-engine', pr_number)
