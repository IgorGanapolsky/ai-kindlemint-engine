#!/usr/bin/env python3
"""
Intelligent Daily Briefing - Assembles context-aware daily operations summary
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class IntelligentDailyBrief:
    """Creates intelligent, context-aware daily briefings from job status files."""
    
    def __init__(self):
        self.status_dir = Path("output/job_status")
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
    def generate_briefing(self) -> Dict[str, Any]:
        """Generate comprehensive daily briefing from job statuses."""
        job_statuses = self._load_job_statuses()
        
        briefing = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._determine_overall_status(job_statuses),
            "executive_summary": self._generate_executive_summary(job_statuses),
            "job_details": job_statuses,
            "key_metrics": self._extract_key_metrics(job_statuses),
            "action_items": self._compile_action_items(job_statuses),
            "business_impact": self._assess_business_impact(job_statuses)
        }
        
        return briefing
        
    def send_slack_briefing(self, briefing: Dict[str, Any]):
        """Send intelligent briefing to Slack."""
        if not self.webhook_url:
            print("⚠️ Slack webhook not configured - briefing not sent")
            return
            
        message = self._format_slack_message(briefing)
        
        try:
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            print("📧 Intelligent Daily Briefing sent to Slack!")
        except Exception as e:
            print(f"❌ Failed to send briefing: {e}")
            
    def _load_job_statuses(self) -> Dict[str, Any]:
        """Load all job status files."""
        statuses = {}
        
        job_files = {
            "market_research": "market-research_status.json",
            "book_publishing": "book-publishing_status.json", 
            "marketing": "marketing-campaigns_status.json",
            "analytics": "analytics-reporting_status.json"
        }
        
        for job_name, filename in job_files.items():
            status_file = self.status_dir / filename
            if status_file.exists():
                try:
                    with open(status_file, 'r') as f:
                        statuses[job_name] = json.load(f)
                except Exception as e:
                    statuses[job_name] = {
                        "status": "unknown",
                        "summary": f"Failed to read status file: {e}"
                    }
            else:
                statuses[job_name] = {
                    "status": "skipped",
                    "summary": "Job did not run today",
                    "skip_reason": "Not scheduled or manually disabled"
                }
                
        return statuses
        
    def _determine_overall_status(self, job_statuses: Dict[str, Any]) -> str:
        """Determine overall operation status."""
        statuses = [job.get("status", "unknown") for job in job_statuses.values()]
        
        if all(s == "success" for s in statuses):
            return "success"
        elif any(s == "failure" for s in statuses):
            return "failure"
        elif any(s == "partial" for s in statuses):
            return "partial"
        elif all(s == "skipped" for s in statuses):
            return "skipped"
        else:
            return "mixed"
            
    def _generate_executive_summary(self, job_statuses: Dict[str, Any]) -> str:
        """Generate executive summary of daily operations."""
        successful_jobs = [name for name, status in job_statuses.items() if status.get("status") == "success"]
        failed_jobs = [name for name, status in job_statuses.items() if status.get("status") == "failure"]
        skipped_jobs = [name for name, status in job_statuses.items() if status.get("status") == "skipped"]
        
        if len(successful_jobs) == len(job_statuses):
            return f"All {len(successful_jobs)} daily operations completed successfully. KindleMint Empire running smoothly."
        elif failed_jobs:
            return f"{len(failed_jobs)} operation(s) failed, {len(successful_jobs)} succeeded. Immediate attention required for: {', '.join(failed_jobs)}."
        elif skipped_jobs:
            return f"{len(successful_jobs)} operations completed, {len(skipped_jobs)} skipped as planned. Normal operations."
        else:
            return "Mixed results across daily operations. Review individual job details."
            
    def _extract_key_metrics(self, job_statuses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key business metrics from job results."""
        metrics = {
            "books_published": 0,
            "revenue_impact": 0,
            "marketing_reach": 0,
            "automation_efficiency": 0
        }
        
        # Extract metrics from each job
        for job_name, status in job_statuses.items():
            job_metrics = status.get("metrics", {})
            
            if job_name == "book_publishing":
                metrics["books_published"] = job_metrics.get("books_published", 0)
                metrics["revenue_impact"] = job_metrics.get("estimated_revenue", 0)
            elif job_name == "marketing":
                metrics["marketing_reach"] = job_metrics.get("posts_created", 0)
            elif job_name == "analytics":
                metrics["automation_efficiency"] = job_metrics.get("uptime_percentage", 0)
                
        return metrics
        
    def _compile_action_items(self, job_statuses: Dict[str, Any]) -> List[str]:
        """Compile action items from all jobs."""
        action_items = []
        
        for job_name, status in job_statuses.items():
            # Add failure-related actions
            if status.get("status") == "failure":
                suggested_actions = status.get("suggested_actions", [])
                action_items.extend([f"[{job_name.title()}] {action}" for action in suggested_actions])
            
            # Add next actions from successful jobs
            elif status.get("status") == "success":
                next_actions = status.get("next_actions", [])
                action_items.extend([f"[{job_name.title()}] {action}" for action in next_actions])
                
        return action_items[:5]  # Limit to top 5 most important
        
    def _assess_business_impact(self, job_statuses: Dict[str, Any]) -> Dict[str, str]:
        """Assess business impact of today's operations."""
        impact = {
            "revenue": "stable",
            "growth": "on_track", 
            "automation": "healthy",
            "market_position": "maintaining"
        }
        
        # Analyze impact based on job results
        publishing_status = job_statuses.get("book_publishing", {})
        if publishing_status.get("status") == "success":
            impact["revenue"] = "positive"
            impact["growth"] = "accelerating"
            
        marketing_status = job_statuses.get("marketing", {})
        if marketing_status.get("status") == "failure":
            impact["market_position"] = "at_risk"
            
        return impact
        
    def _format_slack_message(self, briefing: Dict[str, Any]) -> Dict[str, Any]:
        """Format briefing as Slack message."""
        overall_status = briefing["overall_status"]
        status_emoji = {
            "success": "✅",
            "failure": "❌", 
            "partial": "⚠️",
            "skipped": "⏭️",
            "mixed": "🔄"
        }.get(overall_status, "❓")
        
        # Create detailed job status fields
        job_fields = []
        for job_name, status in briefing["job_details"].items():
            job_emoji = {
                "success": "✅",
                "failure": "❌",
                "partial": "⚠️", 
                "skipped": "⏭️"
            }.get(status.get("status"), "❓")
            
            job_title = job_name.replace("_", " ").title()
            job_summary = status.get("summary", "No details available")
            
            job_fields.append({
                "type": "mrkdwn",
                "text": f"*{job_title}:* {job_emoji}\\n{job_summary}"
            })
            
        # Create metrics section
        metrics = briefing["key_metrics"]
        metrics_text = f"*Books Published:* {metrics['books_published']}\\n*Revenue Impact:* ${metrics['revenue_impact']:.2f}\\n*Automation:* {metrics['automation_efficiency']:.1f}% uptime"
        
        # Create action items
        action_items = briefing.get("action_items", [])
        actions_text = "\\n".join([f"• {item}" for item in action_items[:3]]) if action_items else "No immediate actions required"
        
        message = {
            "text": f"{status_emoji} Intelligent Daily Operations Briefing",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{status_emoji} Intelligent Daily Briefing"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Executive Summary:*\\n{briefing['executive_summary']}"
                    }
                },
                {
                    "type": "section",
                    "fields": job_fields
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*📊 Key Metrics*\\n{metrics_text}"
                        },
                        {
                            "type": "mrkdwn", 
                            "text": f"*🎯 Action Items*\\n{actions_text}"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🤖 KindleMint Empire Intelligence • {briefing['date']} • Business Impact: {briefing['business_impact']['revenue'].title()}"
                        }
                    ]
                }
            ]
        }
        
        return message

def main():
    """Generate and send intelligent daily briefing."""
    print("🧠 Generating Intelligent Daily Briefing...")
    
    briefer = IntelligentDailyBrief()
    briefing = briefer.generate_briefing()
    
    # Save briefing to file
    output_dir = Path("output/daily_briefings")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    briefing_file = output_dir / f"daily_briefing_{briefing['date']}.json"
    with open(briefing_file, 'w') as f:
        json.dump(briefing, f, indent=2, default=str)
        
    print(f"📄 Briefing saved to {briefing_file}")
    
    # Send to Slack
    briefer.send_slack_briefing(briefing)
    
    # Print executive summary
    print(f"📊 Executive Summary: {briefing['executive_summary']}")
    
    return briefing["overall_status"] == "success"

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)