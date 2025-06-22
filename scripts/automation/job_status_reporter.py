#!/usr/bin/env python3
"""
Job Status Reporter - Creates detailed status summaries for GitHub Actions workflow jobs
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class JobStatusReporter:
    """Reports detailed job status for workflow operations."""
    
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.status_dir = Path("output/job_status")
        self.status_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.status_dir / f"{job_name}_status.json"
        
    def report_success(self, summary: str, details: Dict[str, Any] = None, metrics: Dict[str, Any] = None):
        """Report successful job completion with details."""
        status = {
            "job_name": self.job_name,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "details": details or {},
            "metrics": metrics or {},
            "next_actions": []
        }
        self._write_status(status)
        print(f"✅ SUCCESS: {summary}")
        
    def report_failure(self, error_message: str, error_details: str = None, suggested_actions: list = None):
        """Report job failure with error details."""
        status = {
            "job_name": self.job_name,
            "status": "failure", 
            "timestamp": datetime.now().isoformat(),
            "summary": f"Job failed: {error_message}",
            "error_message": error_message,
            "error_details": error_details,
            "suggested_actions": suggested_actions or [],
            "retry_recommended": True
        }
        self._write_status(status)
        print(f"❌ FAILURE: {error_message}")
        
    def report_skipped(self, reason: str, context: str = None):
        """Report job was skipped with reason."""
        status = {
            "job_name": self.job_name,
            "status": "skipped",
            "timestamp": datetime.now().isoformat(),
            "summary": f"Job skipped: {reason}",
            "skip_reason": reason,
            "context": context,
            "impact": "none"
        }
        self._write_status(status)
        print(f"⏭️ SKIPPED: {reason}")
        
    def report_partial(self, summary: str, completed_tasks: list, failed_tasks: list, warnings: list = None):
        """Report partial success with mixed results."""
        status = {
            "job_name": self.job_name,
            "status": "partial",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "warnings": warnings or [],
            "requires_attention": len(failed_tasks) > 0
        }
        self._write_status(status)
        print(f"⚠️ PARTIAL: {summary}")
        
    def _write_status(self, status: Dict[str, Any]):
        """Write status to file."""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2, default=str)

def main():
    """CLI interface for job status reporting."""
    if len(sys.argv) < 4:
        print("Usage: python job_status_reporter.py <job_name> <status_type> <message> [details_json]")
        print("Status types: success, failure, skipped, partial")
        sys.exit(1)
        
    job_name = sys.argv[1]
    status_type = sys.argv[2]
    message = sys.argv[3]
    details = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    
    reporter = JobStatusReporter(job_name)
    
    if status_type == "success":
        reporter.report_success(message, details.get("details"), details.get("metrics"))
    elif status_type == "failure":
        reporter.report_failure(message, details.get("error_details"), details.get("suggested_actions"))
    elif status_type == "skipped":
        reporter.report_skipped(message, details.get("context"))
    elif status_type == "partial":
        reporter.report_partial(message, details.get("completed", []), details.get("failed", []), details.get("warnings"))
    else:
        print(f"Unknown status type: {status_type}")
        sys.exit(1)

if __name__ == "__main__":
    main()