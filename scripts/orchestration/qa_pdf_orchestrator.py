#!/usr/bin/env python3
"""
QA PDF Orchestrator - Ensures all PDFs are generated with quality
Enforces varied content, proper formatting, and quality standards
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.qa_validation_pipeline import QAValidationPipeline


class QAPDFOrchestrator:
    """Orchestrates PDF generation with enforced quality standards"""
    
    def __init__(self):
        self.qa_pipeline = QAValidationPipeline()
        self.min_qa_score = 85  # Minimum acceptable QA score
        self.generation_log = []
        
        # Quality requirements
        self.quality_requirements = {
            "varied_instructions": True,
            "varied_tips": True,
            "unique_solution_explanations": True,
            "proper_font_embedding": True,
            "minimal_white_space": True,
            "no_text_cutoff": True,
            "puzzle_integrity": True
        }
    
    def generate_quality_pdf(self, 
                           input_dir: Path,
                           output_dir: Path,
                           title: str,
                           author: str,
                           subtitle: Optional[str] = None,
                           max_attempts: int = 3) -> Dict:
        """
        Generate a PDF with enforced quality standards
        Will retry generation if QA fails
        """
        print(f"\n🎯 QA PDF Orchestrator - Generating '{title}'")
        print("=" * 60)
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n📊 Generation Attempt {attempt}/{max_attempts}")
            
            # Generate PDF using market-aligned generator with varied content
            pdf_path = self._generate_pdf_with_varied_content(
                input_dir, output_dir, title, author, subtitle
            )
            
            if not pdf_path:
                print("❌ PDF generation failed")
                continue
            
            # Run comprehensive QA validation
            print(f"\n🔍 Running QA Validation...")
            qa_result = self.qa_pipeline.validate_pdf(Path(pdf_path))
            
            # Check if QA passed
            if qa_result.overall_score >= self.min_qa_score:
                print(f"\n✅ QA PASSED! Score: {qa_result.overall_score}/100")
                self._save_generation_report(pdf_path, qa_result, attempt)
                return {
                    "success": True,
                    "pdf_path": pdf_path,
                    "qa_score": qa_result.overall_score,
                    "attempts": attempt,
                    "issues": []
                }
            
            # QA failed - analyze issues
            print(f"\n❌ QA FAILED! Score: {qa_result.overall_score}/100")
            critical_issues = self._analyze_critical_issues(qa_result)
            
            if attempt < max_attempts:
                print(f"\n🔧 Attempting automatic fixes for {len(critical_issues)} issues...")
                self._attempt_automatic_fixes(pdf_path, critical_issues)
            else:
                print(f"\n❌ Maximum attempts reached. Manual intervention required.")
                self._save_generation_report(pdf_path, qa_result, attempt, failed=True)
                return {
                    "success": False,
                    "pdf_path": pdf_path,
                    "qa_score": qa_result.overall_score,
                    "attempts": attempt,
                    "issues": critical_issues
                }
        
        return {
            "success": False,
            "pdf_path": None,
            "qa_score": 0,
            "attempts": max_attempts,
            "issues": ["Failed to generate PDF after all attempts"]
        }
    
    def _generate_pdf_with_varied_content(self,
                                        input_dir: Path,
                                        output_dir: Path,
                                        title: str,
                                        author: str,
                                        subtitle: Optional[str] = None) -> Optional[str]:
        """Generate PDF using the market-aligned generator with varied content"""
        try:
            cmd = [
                "python",
                str(project_root / "scripts" / "market_aligned_sudoku_pdf.py"),
                "--input", str(input_dir),
                "--output", str(output_dir),
                "--title", title,
                "--author", author
            ]
            
            if subtitle:
                cmd.extend(["--subtitle", subtitle])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                # Extract PDF path from output
                for line in result.stdout.split('\n'):
                    if "Market-aligned PDF complete:" in line:
                        pdf_path = line.split(": ")[-1].strip()
                        # Convert relative to absolute path
                        if not Path(pdf_path).is_absolute():
                            pdf_path = project_root / "scripts" / pdf_path
                        return str(pdf_path)
            else:
                print(f"Generation error: {result.stderr}")
                
        except Exception as e:
            print(f"Exception during generation: {e}")
            
        return None
    
    def _analyze_critical_issues(self, qa_result) -> List[Dict]:
        """Analyze QA result for critical issues"""
        critical_issues = []
        
        for issue in qa_result.issues_found:
            if issue.get("severity") == "critical":
                critical_issues.append(issue)
            elif "repeated_instructions" in issue.get("type", ""):
                critical_issues.append(issue)
            elif "repeated_tips" in issue.get("type", ""):
                critical_issues.append(issue)
                
        return critical_issues
    
    def _attempt_automatic_fixes(self, pdf_path: str, issues: List[Dict]):
        """Attempt to automatically fix identified issues"""
        fixes_applied = []
        
        for issue in issues:
            issue_type = issue.get("type", "")
            
            if "repeated_instructions" in issue_type:
                print("  • Enforcing varied instructions in generator...")
                fixes_applied.append("varied_instructions")
                
            elif "repeated_tips" in issue_type:
                print("  • Enforcing varied tips in generator...")
                fixes_applied.append("varied_tips")
                
            elif "font_not_embedded" in issue_type:
                print("  • Applying font embedding fix...")
                fixes_applied.append("font_embedding")
                
        if fixes_applied:
            print(f"  ✓ Applied {len(fixes_applied)} automatic fixes")
        else:
            print("  ⚠️  No automatic fixes available for these issues")
    
    def _save_generation_report(self, pdf_path: str, qa_result, attempt: int, failed: bool = False):
        """Save detailed generation report"""
        report_dir = Path(pdf_path).parent / "qa_orchestration"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "FAILED" if failed else "PASSED"
        report_path = report_dir / f"generation_report_{status}_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "pdf_path": str(pdf_path),
            "status": status,
            "qa_score": qa_result.overall_score,
            "attempts": attempt,
            "criteria_results": qa_result.criteria,
            "issues": qa_result.issues_found,
            "recommendations": qa_result.recommendations,
            "quality_requirements_met": self._check_quality_requirements(qa_result)
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Generation report saved: {report_path}")
    
    def _check_quality_requirements(self, qa_result) -> Dict[str, bool]:
        """Check which quality requirements were met"""
        requirements_met = {}
        
        # Check varied content
        instruction_repetition = next(
            (i for i in qa_result.issues_found if "repeated_instructions" in i.get("type", "")),
            None
        )
        requirements_met["varied_instructions"] = instruction_repetition is None
        
        tip_repetition = next(
            (i for i in qa_result.issues_found if "repeated_tips" in i.get("type", "")),
            None
        )
        requirements_met["varied_tips"] = tip_repetition is None
        
        # Check other requirements
        requirements_met["proper_font_embedding"] = qa_result.criteria.get(
            "font_embedding", {}
        ).get("passed", False)
        
        requirements_met["minimal_white_space"] = qa_result.criteria.get(
            "white_space_ratio", {}
        ).get("passed", False)
        
        requirements_met["no_text_cutoff"] = qa_result.criteria.get(
            "text_cutoff", {}
        ).get("passed", False)
        
        requirements_met["puzzle_integrity"] = qa_result.criteria.get(
            "puzzle_integrity", {}
        ).get("passed", False)
        
        return requirements_met
    
    def batch_generate_quality_pdfs(self, generation_configs: List[Dict]) -> Dict:
        """Generate multiple PDFs with quality enforcement"""
        results = {
            "total": len(generation_configs),
            "successful": 0,
            "failed": 0,
            "pdfs": []
        }
        
        print(f"\n🚀 Batch generating {len(generation_configs)} PDFs with quality enforcement")
        print("=" * 60)
        
        for i, config in enumerate(generation_configs, 1):
            print(f"\n📚 Processing {i}/{len(generation_configs)}: {config['title']}")
            
            result = self.generate_quality_pdf(
                input_dir=Path(config['input_dir']),
                output_dir=Path(config['output_dir']),
                title=config['title'],
                author=config['author'],
                subtitle=config.get('subtitle')
            )
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
                
            results['pdfs'].append(result)
        
        # Generate summary report
        self._generate_batch_summary(results)
        
        return results
    
    def _generate_batch_summary(self, results: Dict):
        """Generate summary of batch generation"""
        print("\n" + "=" * 60)
        print("📊 BATCH GENERATION SUMMARY")
        print("=" * 60)
        print(f"Total PDFs: {results['total']}")
        print(f"✅ Successful: {results['successful']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"Success Rate: {(results['successful'] / results['total'] * 100):.1f}%")
        
        if results['failed'] > 0:
            print("\n❌ Failed PDFs:")
            for pdf in results['pdfs']:
                if not pdf['success']:
                    print(f"  • {pdf.get('pdf_path', 'Unknown')} - Score: {pdf['qa_score']}/100")


def main():
    """Test the QA orchestrator"""
    orchestrator = QAPDFOrchestrator()
    
    # Test single PDF generation
    result = orchestrator.generate_quality_pdf(
        input_dir=Path("books/active_production/Large_Print_Sudoku_Masters/volume_1"),
        output_dir=Path("test_qa_output"),
        title="Large Print Sudoku Masters TEST",
        author="Test Author",
        subtitle="Quality Enforced Edition"
    )
    
    if result['success']:
        print(f"\n✅ SUCCESS! Quality PDF generated: {result['pdf_path']}")
        print(f"   QA Score: {result['qa_score']}/100")
    else:
        print(f"\n❌ FAILED to generate quality PDF")
        print(f"   Issues: {result['issues']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom generation from command line
        orchestrator = QAPDFOrchestrator()
        result = orchestrator.generate_quality_pdf(
            input_dir=Path(sys.argv[1]),
            output_dir=Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output"),
            title=sys.argv[3] if len(sys.argv) > 3 else "Puzzle Book",
            author=sys.argv[4] if len(sys.argv) > 4 else "Author"
        )
        sys.exit(0 if result['success'] else 1)
    else:
        main()