#!/usr/bin/env python3
"""
Claude Artifacts QA Interface
Generates interactive QA reports for Claude Artifacts workspace
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class QAArtifactsInterface:
    """Generate Claude Artifacts-compatible QA visualizations"""

    def __init__(self):
        self.artifact_template = """
<!DOCTYPE html>
<html>
<head>
    <title>QA Report - {title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .qa-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .qa-header {{
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .qa-score {{
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        .qa-score.pass {{
            color: #4caf50;
        }}
        .qa-score.fail {{
            color: #f44336;
        }}
        .criteria-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .criterion-card {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            position: relative;
        }}
        .criterion-card.pass {{
            border-left: 4px solid #4caf50;
        }}
        .criterion-card.fail {{
            border-left: 4px solid #f44336;
        }}
        .criterion-card h3 {{
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .status-icon {{
            font-size: 24px;
        }}
        .issues-section {{
            margin-top: 40px;
            padding: 20px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
        }}
        .issue-item {{
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
        }}
        .recommendations {{
            margin-top: 40px;
            padding: 20px;
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 8px;
        }}
        .page-preview {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }}
        .page-thumb {{
            border: 1px solid #e0e0e0;
            padding: 10px;
            text-align: center;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .page-thumb:hover {{
            border-color: #2196f3;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .page-thumb.issue {{
            border-color: #f44336;
            background: #ffebee;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
        }}
        .metric-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }}
        .metric-fill {{
            height: 100%;
            background: #2196f3;
            transition: width 0.3s;
        }}
        .metric-fill.good {{
            background: #4caf50;
        }}
        .metric-fill.warning {{
            background: #ff9800;
        }}
        .metric-fill.bad {{
            background: #f44336;
        }}
    </style>
</head>
<body>
    <div class="qa-container">
        <div class="qa-header">
            <h1>📊 QA Validation Report</h1>
            <p><strong>Book:</strong> {book_name}</p>
            <p><strong>Generated:</strong> {timestamp}</p>
            <div class="qa-score {score_class}">{overall_score}/100</div>
            <p style="text-align: center; font-size: 20px;">
                {status_message}
            </p>
        </div>
        
        <div class="criteria-grid">
            {criteria_cards}
        </div>
        
        {issues_section}
        
        {recommendations_section}
        
        <div class="page-preview">
            <h2>📄 Page Analysis</h2>
            {page_previews}
        </div>
    </div>
    
    <script>
        // Interactive features for Claude Artifacts
        function highlightIssue(pageNum) {{
            console.log('Highlighting issues on page', pageNum);
            // This would connect to Claude's interface
        }}
        
        function requestFix(issueType) {{
            console.log('Requesting fix for', issueType);
            // This would trigger Claude to suggest fixes
        }}
    </script>
</body>
</html>
"""

    def generate_qa_artifact(self, qa_result: Dict, pdf_path: Path) -> str:
        """Generate HTML artifact for Claude interface"""

        # Determine pass/fail status
        passed = qa_result.get("passed", False)
        score = qa_result.get("overall_score", 0)

        # Generate criteria cards
        criteria_cards = []
        for criterion, details in qa_result.get("criteria", {}).items():
            status = "pass" if details.get("passed", False) else "fail"
            icon = "✅" if details.get("passed", False) else "❌"

            card = f"""
            <div class="criterion-card {status}">
                <h3>
                    <span class="status-icon">{icon}</span>
                    {criterion.replace('_', ' ').title()}
                </h3>
                <div class="metric">
                    <span>Score: {details.get('score', 0)}</span>
                    <span>Threshold: {details.get('threshold', 0)}</span>
                </div>
                <div class="metric-bar">
                    <div class="metric-fill {self._get_metric_class(details)}" 
                         style="width: {self._get_metric_width(details)}%"></div>
                </div>
            </div>
            """
            criteria_cards.append(card)

        # Generate issues section
        issues = qa_result.get("issues_found", [])
        issues_html = ""
        if issues:
            issue_items = []
            for issue in issues[:10]:  # Show top 10
                issue_items.append(
                    f"""
                <div class="issue-item">
                    <strong>{issue.get('type', 'Unknown')}:</strong>
                    {issue.get('message', str(issue))}
                    <button onclick="requestFix('{issue.get('type', '')}')">
                        🔧 Request Fix
                    </button>
                </div>
                """
                )

            issues_html = f"""
            <div class="issues-section">
                <h2>⚠️ Issues Found ({len(issues)})</h2>
                {''.join(issue_items)}
            </div>
            """

        # Generate recommendations
        recommendations = qa_result.get("recommendations", [])
        rec_html = ""
        if recommendations:
            rec_items = ["<li>" + rec + "</li>" for rec in recommendations]
            rec_html = f"""
            <div class="recommendations">
                <h2>💡 Recommendations</h2>
                <ul>
                    {''.join(rec_items)}
                </ul>
            </div>
            """

        # Generate page previews (mock for now)
        page_previews = []
        for i in range(1, 11):  # Show first 10 pages
            has_issue = i in [3, 7]  # Mock pages with issues
            page_class = "issue" if has_issue else ""
            page_previews.append(
                f"""
            <div class="page-thumb {page_class}" onclick="highlightIssue({i})">
                <div>Page {i}</div>
                {'⚠️' if has_issue else '✓'}
            </div>
            """
            )

        # Fill template
        html = self.artifact_template.format(
            title=pdf_path.name,
            book_name=pdf_path.name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            overall_score=score,
            score_class="pass" if passed else "fail",
            status_message="✅ Ready for Production" if passed else "❌ Requires Fixes",
            criteria_cards="\n".join(criteria_cards),
            issues_section=issues_html,
            recommendations_section=rec_html,
            page_previews="\n".join(page_previews),
        )

        return html

    def _get_metric_class(self, details: Dict) -> str:
        """Determine color class for metric bar"""
        if details.get("passed", False):
            return "good"
        score = details.get("score", 0)
        threshold = details.get("threshold", 0)

        # Calculate how far from threshold
        if threshold > 0:
            ratio = score / threshold
            if ratio > 0.8:
                return "warning"
        return "bad"

    def _get_metric_width(self, details: Dict) -> float:
        """Calculate metric bar width percentage"""
        score = details.get("score", 0)
        threshold = details.get("threshold", 100)

        if threshold > 0:
            return min(100, (score / threshold) * 100)
        return 0

    def save_artifact(self, html: str, output_path: Path):
        """Save HTML artifact to file"""
        with open(output_path, "w") as f:
            f.write(html)
        print(f"📄 QA Artifact saved to: {output_path}")

    def generate_markdown_summary(self, qa_result: Dict) -> str:
        """Generate markdown summary for Claude chat"""

        passed = qa_result.get("passed", False)
        score = qa_result.get("overall_score", 0)

        summary = f"""## QA Validation Results

**Overall Score:** {score}/100 {'✅ PASSED' if passed else '❌ FAILED'}

### Criteria Breakdown:
"""

        for criterion, details in qa_result.get("criteria", {}).items():
            status = "✅" if details.get("passed", False) else "❌"
            summary += f"- {status} **{criterion}**: {details.get('score', 0)} (threshold: {details.get('threshold', 0)})\n"

        if qa_result.get("issues_found"):
            summary += (
                f"\n### Issues Found ({len(qa_result.get('issues_found', []))}):\n"
            )
            for issue in qa_result.get("issues_found", [])[:5]:
                summary += f"- {issue.get('type', 'Unknown')}: {issue.get('message', str(issue))}\n"

        if qa_result.get("recommendations"):
            summary += "\n### Recommendations:\n"
            for rec in qa_result.get("recommendations", []):
                summary += f"- {rec}\n"

        return summary


def main():
    """Test the artifacts interface"""
    # Mock QA result for testing
    mock_result = {
        "passed": False,
        "overall_score": 73.5,
        "criteria": {
            "duplicate_content": {"score": 15, "threshold": 10, "passed": False},
            "text_cutoff": {"score": 0, "threshold": 0, "passed": True},
            "white_space_ratio": {"score": 89, "threshold": 92, "passed": True},
            "puzzle_integrity": {"score": 95, "threshold": 100, "passed": False},
            "font_embedding": {"score": 100, "threshold": 100, "passed": True},
        },
        "issues_found": [
            {"type": "duplicate_content", "message": "15% duplicate text found"},
            {"type": "puzzle_integrity", "message": "5 puzzles missing answer keys"},
        ],
        "recommendations": [
            "Remove duplicate clues in puzzles 12-18",
            "Add missing answer keys for puzzles 45-50",
        ],
    }

    interface = QAArtifactsInterface()
    html = interface.generate_qa_artifact(mock_result, Path("test_book.pdf"))

    # Save test artifact
    output_path = Path("qa_artifact_test.html")
    interface.save_artifact(html, output_path)

    # Print markdown summary
    print(interface.generate_markdown_summary(mock_result))


if __name__ == "__main__":
    main()
