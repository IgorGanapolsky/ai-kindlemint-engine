#!/usr/bin/env python3
"""
Integrated PDF Validator
Combines all PDF validation: content, metadata, and visual QA
"""

import sys
from pathlib import Path
from typing import Dict
import json
from datetime import datetime

# Import existing validators
from .sudoku_content_validator import SudokuContentValidator
from .pdf_visual_qa_validator import PDFVisualQAValidator


class IntegratedPDFValidator:
    """Complete PDF validation including visual QA"""
    
    def __init__(self):
        self.content_validator = SudokuContentValidator()
        self.visual_validator = PDFVisualQAValidator()
        self.reports = []
        
    def validate_pdf_complete(self, pdf_path: Path) -> Dict:
        """Run all validation checks on a PDF"""
        print(f"\n{'='*60}")
        print(f"🔍 COMPLETE PDF VALIDATION: {pdf_path.name}")
        print(f"{'='*60}\n")
        
        overall_report = {
            "pdf_path": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
            "overall_status": "PASS",
            "validation_results": {}
        }
        
        # 1. Content Validation (puzzle correctness)
        print("📋 Step 1/2: Content Validation...")
        try:
            content_report = self.content_validator.validate_puzzle_book(pdf_path)
            overall_report["validation_results"]["content"] = {
                "status": content_report.get("status", "ERROR"),
                "errors": len(content_report.get("errors", [])),
                "warnings": len(content_report.get("warnings", [])),
                "details": content_report
            }
            if content_report.get("status") == "FAIL":
                overall_report["overall_status"] = "FAIL"
        except Exception as e:
            overall_report["validation_results"]["content"] = {
                "status": "ERROR",
                "error": str(e)
            }
            overall_report["overall_status"] = "FAIL"
            
        # 2. Visual QA Validation (layout, overlaps, margins)
        print("\n🎨 Step 2/2: Visual QA Validation...")
        try:
            visual_report = self.visual_validator.validate_pdf_visual_quality(pdf_path, save_report=False)
            overall_report["validation_results"]["visual"] = {
                "status": visual_report.get("status", "ERROR"),
                "text_overlaps": len(visual_report.get("text_overlaps", [])),
                "margin_violations": len(visual_report.get("margin_violations", [])),
                "layout_issues": len(visual_report.get("layout_violations", [])),
                "details": visual_report
            }
            if visual_report.get("status") == "FAIL":
                overall_report["overall_status"] = "FAIL"
        except Exception as e:
            overall_report["validation_results"]["visual"] = {
                "status": "ERROR", 
                "error": str(e)
            }
            overall_report["overall_status"] = "FAIL"
            
        # Generate summary
        overall_report["summary"] = self._generate_summary(overall_report)
        
        # Save comprehensive report
        report_path = pdf_path.parent / f"{pdf_path.stem}_complete_validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(overall_report, f, indent=2)
            
        # Print results
        self._print_results(overall_report)
        
        return overall_report
        
    def _generate_summary(self, report: Dict) -> Dict:
        """Generate executive summary of all issues"""
        summary = {
            "total_issues": 0,
            "critical_issues": [],
            "major_issues": [],
            "minor_issues": []
        }
        
        # Content issues
        content = report["validation_results"].get("content", {})
        if content.get("status") == "FAIL":
            details = content.get("details", {})
            for error in details.get("errors", []):
                summary["critical_issues"].append(f"Content: {error}")
                summary["total_issues"] += 1
                
        # Visual issues
        visual = report["validation_results"].get("visual", {})
        if visual.get("status") == "FAIL":
            details = visual.get("details", {})
            
            # Text overlaps are critical
            for overlap in details.get("text_overlaps", []):
                summary["critical_issues"].append(
                    f"Page {overlap['page']}: Text overlap - '{overlap['text1']}' overlaps '{overlap['text2']}'"
                )
                summary["total_issues"] += 1
                
            # Margin violations are major
            for violation in details.get("margin_violations", []):
                summary["major_issues"].append(
                    f"Page {violation['page']}: {violation['type']} - expected {violation['expected']}, got {violation['actual']}"
                )
                summary["total_issues"] += 1
                
            # Layout issues are minor
            for issue in details.get("layout_violations", []):
                summary["minor_issues"].append(
                    f"Page {issue['page']}: {issue['type']}"
                )
                summary["total_issues"] += 1
                
        return summary
        
    def _print_results(self, report: Dict):
        """Print formatted validation results"""
        print("\n" + "="*60)
        print("📊 VALIDATION RESULTS")
        print("="*60)
        
        print(f"\n🎯 Overall Status: {report['overall_status']}")
        
        # Content results
        content = report["validation_results"].get("content", {})
        print(f"\n📋 Content Validation: {content.get('status', 'N/A')}")
        if content.get("errors", 0) > 0:
            print(f"   ❌ Errors: {content['errors']}")
        if content.get("warnings", 0) > 0:
            print(f"   ⚠️  Warnings: {content['warnings']}")
            
        # Visual results
        visual = report["validation_results"].get("visual", {})
        print(f"\n🎨 Visual QA: {visual.get('status', 'N/A')}")
        if visual.get("text_overlaps", 0) > 0:
            print(f"   ❌ Text Overlaps: {visual['text_overlaps']}")
        if visual.get("margin_violations", 0) > 0:
            print(f"   ❌ Margin Violations: {visual['margin_violations']}")
        if visual.get("layout_issues", 0) > 0:
            print(f"   ⚠️  Layout Issues: {visual['layout_issues']}")
            
        # Summary
        summary = report.get("summary", {})
        if summary.get("total_issues", 0) > 0:
            print(f"\n⚠️  Total Issues Found: {summary['total_issues']}")
            
            if summary.get("critical_issues"):
                print("\n🔴 CRITICAL ISSUES:")
                for issue in summary["critical_issues"][:5]:  # Show first 5
                    print(f"   • {issue}")
                if len(summary["critical_issues"]) > 5:
                    print(f"   ... and {len(summary['critical_issues']) - 5} more")
                    
            if summary.get("major_issues"):
                print("\n🟡 MAJOR ISSUES:")
                for issue in summary["major_issues"][:3]:
                    print(f"   • {issue}")
                if len(summary["major_issues"]) > 3:
                    print(f"   ... and {len(summary['major_issues']) - 3} more")
        else:
            print("\n✅ No issues found - PDF passed all validations!")
            
        print("\n" + "="*60)


def validate_pdf_with_visual_qa(pdf_path: Path) -> bool:
    """Quick validation function that returns pass/fail"""
    validator = IntegratedPDFValidator()
    report = validator.validate_pdf_complete(pdf_path)
    return report["overall_status"] == "PASS"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python integrated_pdf_validator.py <pdf_path>")
        sys.exit(1)
        
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)
        
    validator = IntegratedPDFValidator()
    report = validator.validate_pdf_complete(pdf_path)
    
    # Exit with appropriate code
    sys.exit(0 if report["overall_status"] == "PASS" else 1)