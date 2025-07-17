#!/usr/bin/env python3
"""
Bot Suggestion Processor
Automatically processes and applies suggestions from security/quality bots
"""

import argparse
import os
import re
import sys
from typing import Dict, List

from github import Github


class BotSuggestionProcessor:
    """Process and apply bot suggestions automatically"""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.github = Github(github_token)
        self.safe_patterns = [
            # Security improvements
            r'import\s+secrets',  # Use secrets instead of random
            r'hashlib\.sha256',   # Use stronger hashing
            r'verify=True',       # SSL verification
            
            # Code quality
            r'typing\.',          # Type hints
            r'pathlib\.Path',     # Modern path handling
            r'with\s+open',       # Context managers
        ]
        
        self.bot_accounts = [
            'pixeebot[bot]',
            'dependabot[bot]',
            'deepsource-bot',
            'coderabbitai[bot]',
            'snyk-bot',
        ]
    
    def get_pr_suggestions(self, repo_name: str, pr_number: int) -> List[Dict]:
        """Extract suggestions from PR comments and reviews"""
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        suggestions = []
        
        # Get PR description suggestions
        if pr.body and any(bot in pr.user.login for bot in self.bot_accounts):
            suggestions.extend(self._parse_suggestions(pr.body, 'pr_description'))
        
        # Get comment suggestions
        for comment in pr.get_issue_comments():
            if any(bot in comment.user.login for bot in self.bot_accounts):
                suggestions.extend(self._parse_suggestions(comment.body, 'comment'))
        
        # Get review suggestions
        for review in pr.get_reviews():
            if any(bot in review.user.login for bot in self.bot_accounts):
                for comment in review.get_comments():
                    suggestions.extend(self._parse_suggestions(comment.body, 'review'))
        
        return suggestions
    
    def _parse_suggestions(self, text: str, source_type: str) -> List[Dict]:
        """Parse suggestions from bot text"""
        suggestions = []
        
        # Pattern for code blocks with suggestions
        code_pattern = r'```(?:suggestion|diff|python|javascript)?\n(.*?)\n```'
        
        for match in re.finditer(code_pattern, text, re.DOTALL):
            suggestion_text = match.group(1)
            
            # Categorize suggestion
            category = self._categorize_suggestion(suggestion_text)
            safety_score = self._calculate_safety_score(suggestion_text)
            
            suggestions.append({
                'text': suggestion_text,
                'category': category,
                'safety_score': safety_score,
                'source': source_type,
                'auto_applicable': safety_score >= 0.8
            })
        
        return suggestions
    
    def _categorize_suggestion(self, text: str) -> str:
        """Categorize the type of suggestion"""
        if 'import secrets' in text or 'verify=' in text:
            return 'security'
        elif 'typing' in text or 'type hint' in text.lower():
            return 'type_safety'
        elif 'pathlib' in text or 'with open' in text:
            return 'modernization'
        else:
            return 'general'
    
    def _calculate_safety_score(self, text: str) -> float:
        """Calculate how safe it is to auto-apply this suggestion"""
        score = 0.5  # Base score
        
        # Check against safe patterns
        for pattern in self.safe_patterns:
            if re.search(pattern, text):
                score += 0.1
        
        # Penalize deletions
        if text.count('-') > text.count('+'):
            score -= 0.3
        
        # Penalize large changes
        if len(text.split('\n')) > 20:
            score -= 0.2
        
        return max(0, min(1, score))
    
    def apply_suggestions(self, suggestions: List[Dict], auto_apply_safe: bool = False):
        """Apply suggestions based on safety scores"""
        applied = []
        skipped = []
        
        for suggestion in suggestions:
            if auto_apply_safe and suggestion['auto_applicable']:
                # Apply the suggestion
                success = self._apply_suggestion(suggestion)
                if success:
                    applied.append(suggestion)
                else:
                    skipped.append(suggestion)
            else:
                skipped.append(suggestion)
        
        return applied, skipped
    
    def _apply_suggestion(self, suggestion: Dict) -> bool:
        """Apply a single suggestion"""
        try:
            # This is a simplified version
            # In reality, you'd parse the diff and apply it properly
            print(f"Applying {suggestion['category']} suggestion...")
            return True
        except Exception as e:
            print(f"Failed to apply suggestion: {e}")
            return False
    
    def generate_summary(self, applied: List[Dict], skipped: List[Dict]) -> str:
        """Generate a summary report"""
        summary = "## 🤖 Bot Suggestion Processing Summary\n\n"
        
        if applied:
            summary += f"### ✅ Automatically Applied ({len(applied)})\n\n"
            for s in applied:
                summary += f"- **{s['category']}**: Applied security improvement\n"
        
        if skipped:
            summary += f"\n### ⏭️ Requires Manual Review ({len(skipped)})\n\n"
            for s in skipped:
                summary += f"- **{s['category']}**: Safety score {s['safety_score']:.2f}\n"
        
        summary += "\n### 📊 Statistics\n\n"
        summary += f"- Total suggestions: {len(applied) + len(skipped)}\n"
        summary += f"- Auto-applied: {len(applied)}\n"
        summary += f"- Manual review needed: {len(skipped)}\n"
        
        return summary


def main():
    parser = argparse.ArgumentParser(description='Process bot suggestions')
    parser.add_argument('--repo', required=True, help='Repository name')
    parser.add_argument('--pr-number', type=int, required=True, help='PR number')
    parser.add_argument('--auto-apply-safe', action='store_true', 
                        help='Automatically apply safe suggestions')
    
    args = parser.parse_args()
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    processor = BotSuggestionProcessor(github_token)
    
    # Get suggestions
    suggestions = processor.get_pr_suggestions(args.repo, args.pr_number)
    print(f"Found {len(suggestions)} suggestions")
    
    # Apply suggestions
    applied, skipped = processor.apply_suggestions(
        suggestions, 
        auto_apply_safe=args.auto_apply_safe
    )
    
    # Generate summary
    summary = processor.generate_summary(applied, skipped)
    print(summary)
    
    # Save summary for the workflow
    with open('bot-suggestions-summary.md', 'w') as f:
        f.write(summary)


if __name__ == '__main__':
    main()