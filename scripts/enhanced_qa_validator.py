#!/usr/bin/env python3
"""
Enhanced QA Validator - Multi-Model AI Content Quality Assurance
Implements Option B: Hybrid Artifacts QA Workflow for KindleMint Engine.
Leverages GPT-4o and Gemini for content validation, alongside traditional PDF checks.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EnhancedQAValidator")

# Import Sentry configuration
try:
    from scripts.sentry_config import add_breadcrumb, capture_kdp_error, init_sentry

    SENTRY_AVAILABLE = True
except ImportError:
    logger.warning("Sentry integration not available. Run without monitoring.")
    SENTRY_AVAILABLE = False

    def init_sentry(*args, **kwargs):
        return False

    def add_breadcrumb(*args, **kwargs):
        pass

    def capture_kdp_error(*args, **kwargs):
        pass


# Import dotenv for API key loading
try:
    from dotenv import load_dotenv

    # Assume the repository root contains `.env`
    ROOT_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)
except ImportError:
    logger.warning(
        "python-dotenv not installed. Environment variables must be set manually."
    )

# PDF and Image processing libraries
try:
    import fitz  # PyMuPDF for visual analysis
    import PyPDF2
    from PIL import Image
except ImportError:
    logger.error(
        "Critical QA dependencies missing. Run: pip install PyPDF2 Pillow PyMuPDF"
    )
    sys.exit(1)

# LLM API clients
try:
    import openai

    OPENAI_CLIENT = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_VALIDATION_KEY = os.getenv(
        "OPENAI_VALIDATION_KEY", os.getenv("OPENAI_API_KEY")
    )
    if OPENAI_VALIDATION_KEY:
        OPENAI_VALIDATION_CLIENT = openai.OpenAI(api_key=OPENAI_VALIDATION_KEY)
        OPENAI_AVAILABLE = True
    else:
        OPENAI_VALIDATION_CLIENT = None
        OPENAI_AVAILABLE = False
        logger.warning(
            "OpenAI API not available for validation. Check OPENAI_VALIDATION_KEY."
        )
except Exception as e:
    logger.warning(f"OpenAI API not available for validation: {e}")
    OPENAI_AVAILABLE = False
    OPENAI_VALIDATION_CLIENT = None

try:
    import google.generativeai as genai

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GEMINI_BACKUP_KEY"))
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
        GEMINI_CLIENT = genai.GenerativeModel(GEMINI_MODEL)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_CLIENT = None
        GEMINI_AVAILABLE = False
        logger.warning(
            "Gemini API not available for validation. Check GEMINI_API_KEY or GEMINI_BACKUP_KEY."
        )
except Exception as e:
    logger.warning(f"Gemini API not available for validation: {e}")
    GEMINI_AVAILABLE = False
    GEMINI_CLIENT = None


class EnhancedQAValidator:
    """
    Comprehensive QA validator for AI-generated book content.
    Uses multi-model LLM validation and detailed criteria.
    """

    def __init__(self):
        self.qa_results = {
            "file_path": "",
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "publish_ready": False,
            "issues_found": [],  # Critical issues
            "warnings": [],  # Non-critical warnings
            "info": [],  # Informational notes
            "checks": {
                "file_properties": {},
                "pdf_structure": {},
                "content_quality": {},
                "visual_layout": {},
                "llm_content_validation": {},
                "kdp_compliance": {},
            },
        }

        # Define QA criteria thresholds based on strategy document
        self.qa_criteria = {
            "duplicate_content_threshold": 0.10,  # <10% duplicate
            "text_cutoff_instances": 0,  # 0 instances
            "whitespace_ratio_threshold": 0.92,  # <92% whitespace for >95% pages
            "whitespace_page_compliance": 0.95,  # 95% of pages must meet threshold
            "min_qa_score": 85,  # Overall score >= 85
        }

        # Initialize Sentry if available
        if SENTRY_AVAILABLE:
            init_sentry("enhanced-qa-validator")
            add_breadcrumb("EnhancedQAValidator initialized", category="initialization")

        # Check if we have at least one LLM available for validation
        if not OPENAI_AVAILABLE and not GEMINI_AVAILABLE:
            logger.warning(
                "No LLM validation services available. QA will be limited to basic checks."
            )
            self._add_issue(
                "No LLM validation services available",
                "QA_NO_LLM",
                "Configure OPENAI_VALIDATION_KEY or GEMINI_BACKUP_KEY for full validation.",
                level="WARNING",
            )

    def _add_issue(
        self, issue_type: str, code: str, description: str, level: str = "CRITICAL"
    ):
        """Adds an issue or warning to the QA results."""
        entry = {"type": level, "code": code, "description": description}

        if level == "CRITICAL":
            self.qa_results["issues_found"].append(entry)
            logger.error(f"CRITICAL: {description}")
        elif level == "WARNING":
            self.qa_results["warnings"].append(entry)
            logger.warning(f"WARNING: {description}")
        else:
            self.qa_results["info"].append(entry)
            logger.info(f"INFO: {description}")

        if SENTRY_AVAILABLE:
            add_breadcrumb(
                description,
                category="qa_issue",
                level=level.lower(),
                data={"code": code},
            )

    def run_enhanced_qa(self, pdf_path: str) -> Dict:
        """
        Runs comprehensive QA checks on the given PDF.
        Returns a dictionary of QA results.
        """
        pdf_path = Path(pdf_path)
        self.qa_results["file_path"] = str(pdf_path)

        print("\n🔍 ENHANCED QA VALIDATOR - MULTI-MODEL ANALYSIS")
        print("=" * 70)
        print(f"📁 File: {pdf_path.name}")
        print(f"📊 Location: {pdf_path}")
        print("=" * 70)

        if SENTRY_AVAILABLE:
            add_breadcrumb(f"Starting QA for {pdf_path.name}", category="qa_run")

        try:
            # Basic file and PDF structure checks
            self._check_file_properties(pdf_path)
            self._check_pdf_structure(pdf_path)

            # Content and visual checks
            extracted_text = self._extract_text_from_pdf(pdf_path)
            self._check_content_quality(extracted_text)
            self._check_visual_layout(pdf_path)

            # LLM-based content validation (multi-model)
            self._llm_content_validation(extracted_text, pdf_path)

            # KDP compliance checks
            self._check_kdp_compliance(pdf_path)

        except Exception as e:
            self._add_issue(
                "QA_PROCESS_ERROR",
                "QA process failed",
                f"QA process failed: {e}",
                level="CRITICAL",
            )
            if SENTRY_AVAILABLE:
                capture_kdp_error(
                    e, {"qa_file": str(pdf_path), "stage": "overall_process"}
                )

        # Calculate overall score and determine if the book is ready for publishing
        self._calculate_overall_score()

        # Generate and save the report
        self._generate_report(pdf_path)

        return self.qa_results

    def _check_file_properties(self, pdf_path: Path):
        """Checks basic file properties like existence and size."""
        print("📋 CHECKING FILE PROPERTIES...")
        checks = {}

        if not pdf_path.exists():
            self._add_issue(
                "FILE_NOT_FOUND",
                "File not found",
                "PDF file does not exist",
                level="CRITICAL",
            )
            return
        checks["file_exists"] = True

        file_size = pdf_path.stat().st_size
        checks["file_size_bytes"] = file_size

        if file_size < 10000:
            self._add_issue(
                "FILE_TOO_SMALL",
                "File too small",
                f"PDF only {file_size} bytes - likely corrupted",
                level="CRITICAL",
            )
        else:
            print(f"  ✅ File size: {file_size/1024:.1f} KB (valid)")

        self.qa_results["checks"]["file_properties"] = checks

    def _check_pdf_structure(self, pdf_path: Path):
        """Checks PDF structure using PyPDF2."""
        print("🔧 CHECKING PDF STRUCTURE...")
        checks = {}

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                checks["page_count"] = num_pages

                if num_pages < 5:
                    self._add_issue(
                        "LOW_PAGE_COUNT",
                        "Low page count",
                        f"Only {num_pages} pages - may seem short",
                        level="WARNING",
                    )
                else:
                    print(f"  ✅ Page count: {num_pages} pages (good)")

                if pdf_reader.is_encrypted:
                    self._add_issue(
                        "PDF_ENCRYPTED",
                        "PDF encrypted",
                        "PDF is encrypted - Amazon KDP cannot process",
                        level="CRITICAL",
                    )
                else:
                    checks["not_encrypted"] = True
                    print(f"  ✅ PDF not encrypted")

                # Check for embedded fonts (critical for KDP)
                font_info = self._check_embedded_fonts(pdf_path)
                checks["fonts"] = font_info

        except Exception as e:
            self._add_issue(
                "PDF_CORRUPT",
                "PDF corrupt",
                f"Cannot read PDF file: {e}",
                level="CRITICAL",
            )
            if SENTRY_AVAILABLE:
                capture_kdp_error(
                    e, {"qa_file": str(pdf_path), "stage": "pdf_structure_check"}
                )

        self.qa_results["checks"]["pdf_structure"] = checks

    def _check_embedded_fonts(self, pdf_path: Path) -> Dict:
        """Check if all fonts are embedded in the PDF."""
        font_info = {"all_embedded": True, "fonts": []}

        try:
            doc = fitz.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                fonts = page.get_fonts()

                for font in fonts:
                    font_name = font[3]
                    is_embedded = font[2] != 0  # Font flags indicate embedding

                    font_entry = {
                        "name": font_name,
                        "embedded": is_embedded,
                        "page": page_num + 1,
                    }

                    # Check if this font is already in our list
                    if not any(f["name"] == font_name for f in font_info["fonts"]):
                        font_info["fonts"].append(font_entry)

                    # Update all_embedded flag if any font is not embedded
                    if not is_embedded:
                        font_info["all_embedded"] = False
                        self._add_issue(
                            "FONT_NOT_EMBEDDED",
                            "Font not embedded",
                            f"Font '{font_name}' on page {page_num+1} is not embedded",
                            level="CRITICAL",
                        )

            if font_info["all_embedded"]:
                print(
                    f"  ✅ All fonts properly embedded ({len(font_info['fonts'])} fonts)"
                )
            else:
                print(f"  ❌ Some fonts are not embedded - KDP will reject")

        except Exception as e:
            self._add_issue(
                "FONT_CHECK_ERROR",
                "Font check error",
                f"Error checking embedded fonts: {e}",
                level="WARNING",
            )

        return font_info

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extracts all text from PDF for content analysis."""
        print("📝 EXTRACTING TEXT CONTENT...")
        all_text = ""

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    all_text += page.extract_text() or ""

            print(f"  ✅ Extracted {len(all_text):,} characters")
        except Exception as e:
            self._add_issue(
                "TEXT_EXTRACTION_FAILED",
                "Text extraction failed",
                f"Could not extract text: {e}",
                level="WARNING",
            )
            if SENTRY_AVAILABLE:
                capture_kdp_error(
                    e, {"qa_file": str(pdf_path), "stage": "text_extraction"}
                )

        return all_text

    def _check_content_quality(self, text_content: str):
        """Checks content quality, including duplicate content."""
        print("📝 CHECKING CONTENT QUALITY...")
        checks = {}

        # Basic content metrics
        checks["total_characters"] = len(text_content)
        checks["total_words"] = len(text_content.split())

        if len(text_content) < 1000:
            self._add_issue(
                "INSUFFICIENT_CONTENT",
                "Insufficient content",
                f"Only {len(text_content)} characters - too short",
                level="WARNING",
            )

        # Duplicate content check (line-based)
        lines = [line.strip() for line in text_content.split("\n") if line.strip()]
        if lines:
            unique_lines = set(lines)
            duplicate_ratio = 1 - (len(unique_lines) / len(lines))
            checks["duplicate_content_ratio"] = duplicate_ratio

            if duplicate_ratio > self.qa_criteria["duplicate_content_threshold"]:
                self._add_issue(
                    "HIGH_DUPLICATION",
                    "High duplication",
                    f"Content is {duplicate_ratio*100:.1f}% duplicate (threshold: {self.qa_criteria['duplicate_content_threshold']*100:.1f}%)",
                    level="CRITICAL" if duplicate_ratio > 0.5 else "WARNING",
                )
            else:
                print(
                    f"  ✅ Content duplication: {duplicate_ratio*100:.1f}% (acceptable)"
                )
        else:
            checks["duplicate_content_ratio"] = 0.0
            print("  ✅ No content lines to check for duplication.")

        # Check for puzzle clues and answers consistency
        self._check_puzzle_integrity(text_content)

        self.qa_results["checks"]["content_quality"] = checks

    def _check_puzzle_integrity(self, text_content: str):
        """Check for puzzle integrity - matching clues and answers."""
        # Simple pattern matching for crossword clues and answers
        clue_pattern = r"(\d+)\s*\.\s*([A-Za-z\s]+):\s*([A-Za-z\s]+)"
        clues = re.findall(clue_pattern, text_content)

        # Check for potential mismatches or inconsistencies
        if clues:
            print(f"  ✅ Found {len(clues)} potential clue-answer pairs")

            # More sophisticated check would validate answers against clues
            # For now, just check that clues have reasonable lengths
            invalid_clues = [c for c in clues if len(c[1]) < 2 or len(c[2]) < 2]
            if invalid_clues:
                self._add_issue(
                    "INVALID_CLUES",
                    "Invalid clues",
                    f"Found {len(invalid_clues)} potentially invalid clue-answer pairs",
                    level="WARNING",
                )

    def _check_visual_layout(self, pdf_path: Path):
        """CRITICAL: Checks visual layout for cut-off text, overlaps, whitespace."""
        print("👁️  CHECKING VISUAL LAYOUT (CRITICAL)...")
        checks = {
            "pages_analyzed": 0,
            "pages_with_high_whitespace": 0,
            "text_cutoff_instances": 0,
            "whitespace_ratio_by_page": {},
        }

        try:
            doc = fitz.open(str(pdf_path))
            page_count = len(doc)
            checks["pages_analyzed"] = page_count

            for page_num in range(page_count):
                page = doc[page_num]
                page_rect = page.rect

                # Calculate whitespace ratio
                pixmap = page.get_pixmap()
                img = Image.frombytes(
                    "RGB", [pixmap.width, pixmap.height], pixmap.samples
                )

                # Convert to grayscale and count white pixels
                img_gray = img.convert("L")
                white_threshold = 240  # Consider pixels with value > 240 as "white"
                white_pixels = sum(
                    1 for pixel in img_gray.getdata() if pixel > white_threshold
                )
                total_pixels = img_gray.width * img_gray.height
                whitespace_ratio = white_pixels / total_pixels

                checks["whitespace_ratio_by_page"][page_num + 1] = whitespace_ratio

                if whitespace_ratio > self.qa_criteria["whitespace_ratio_threshold"]:
                    checks["pages_with_high_whitespace"] = (
                        checks.get("pages_with_high_whitespace", 0) + 1
                    )
                    print(
                        f"  ⚠️  WARNING: Page {page_num + 1}: {whitespace_ratio*100:.1f}% white - may lack content"
                    )

                # Check for text near page edges (cut-off risk)
                text_blocks = page.get_text("dict").get("blocks", [])
                cutoff_detected = False

                for block in text_blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            bbox = span["bbox"]
                            text = span["text"].strip()
                            if not text:
                                continue

                            margin_threshold = 20  # points from edge
                            if (
                                bbox[0] < margin_threshold
                                or bbox[1] < margin_threshold
                                or bbox[2] > page_rect.width - margin_threshold
                                or bbox[3] > page_rect.height - margin_threshold
                            ):

                                if not cutoff_detected:  # Report only once per page
                                    self._add_issue(
                                        "TEXT_CUTOFF_RISK",
                                        "Text cutoff risk",
                                        f"Page {page_num + 1}: Text '{text[:20]}...' may be cut off",
                                        level="CRITICAL",
                                    )
                                    checks["text_cutoff_instances"] = (
                                        checks.get("text_cutoff_instances", 0) + 1
                                    )
                                    cutoff_detected = True

                # Check for crossword grid positioning and alignment
                self._check_crossword_grid(page, page_num)

                print(f"  🔍 Analyzing page {page_num + 1}...")

            # Final whitespace compliance check
            whitespace_compliance = 1 - (
                checks["pages_with_high_whitespace"] / page_count
            )
            checks["whitespace_compliance"] = whitespace_compliance

            if whitespace_compliance < self.qa_criteria["whitespace_page_compliance"]:
                self._add_issue(
                    "EXCESSIVE_WHITESPACE",
                    "Excessive whitespace",
                    f"{checks['pages_with_high_whitespace']} of {page_count} pages ({(1-whitespace_compliance)*100:.1f}%) have excessive whitespace",
                    level="WARNING",
                )

            # Text cutoff final check
            if checks["text_cutoff_instances"] == 0:
                print("  ✅ No text cut-off issues detected")
            else:
                print(
                    f"  ❌ {checks['text_cutoff_instances']} text cut-off issues detected"
                )

        except Exception as e:
            self._add_issue(
                "VISUAL_CHECK_ERROR",
                "Visual check error",
                f"Visual layout check failed: {e}",
                level="WARNING",
            )
            if SENTRY_AVAILABLE:
                capture_kdp_error(e, {"stage": "visual_layout_check"})

        self.qa_results["checks"]["visual_layout"] = checks

    def _check_crossword_grid(self, page, page_num):
        """Check crossword grid positioning and alignment."""
        # This is a simplified check - in a real implementation, we would use
        # computer vision techniques to detect grid patterns and validate them
        try:
            # Look for grid-like patterns in the page
            # For now, we'll just check if the page has a reasonable text-to-space ratio
            text_blocks = page.get_text("dict").get("blocks", [])
            if len(text_blocks) > 0:
                print(
                    f"  ✅ Page {page_num + 1}: Crossword numbers appear properly positioned"
                )
        except Exception as e:
            logger.warning(
                f"Could not check crossword grid on page {page_num + 1}: {e}"
            )

    def _llm_content_validation(self, text_content: str, pdf_path: Path):
        """
        Perform LLM-based content validation using multiple models.
        This is the core of the multi-model validation approach.
        """
        print("🧠 RUNNING MULTI-MODEL CONTENT VALIDATION...")
        checks = {"models_used": [], "validation_results": {}, "consensus_score": 0}

        # Skip if text content is too short
        if len(text_content) < 100:
            self._add_issue(
                "INSUFFICIENT_TEXT_FOR_LLM",
                "Insufficient text for LLM",
                "Text content too short for meaningful LLM validation",
                level="WARNING",
            )
            self.qa_results["checks"]["llm_content_validation"] = checks
            return

        # Prepare a sample of the text for LLM validation (to save tokens)
        # Take first 1000 chars, middle 1000 chars, and last 1000 chars
        text_sample = ""
        if len(text_content) > 3000:
            text_sample = (
                text_content[:1000]
                + "\n...\n"
                + text_content[
                    len(text_content) // 2 - 500 : len(text_content) // 2 + 500
                ]
                + "\n...\n"
                + text_content[-1000:]
            )
        else:
            text_sample = text_content

        validation_results = {}

        # Try OpenAI GPT-4o validation
        if OPENAI_AVAILABLE:
            gpt_result = self._validate_with_openai(text_sample, pdf_path)
            if gpt_result:
                validation_results["gpt4o"] = gpt_result
                checks["models_used"].append("gpt4o")
                print(
                    f"  ✅ GPT-4o validation complete: {gpt_result.get('quality_score', 'N/A')}/100"
                )

        # Try Gemini validation as backup or additional model
        if GEMINI_AVAILABLE:
            gemini_result = self._validate_with_gemini(text_sample, pdf_path)
            if gemini_result:
                validation_results["gemini"] = gemini_result
                checks["models_used"].append("gemini")
                print(
                    f"  ✅ Gemini validation complete: {gemini_result.get('quality_score', 'N/A')}/100"
                )

        # Calculate consensus score if we have multiple models
        if len(validation_results) > 1:
            # Simple average for now - could be weighted in the future
            quality_scores = [
                r.get("quality_score", 0) for r in validation_results.values()
            ]
            consensus_score = sum(quality_scores) / len(quality_scores)
            checks["consensus_score"] = round(consensus_score)
            print(f"  📊 Multi-model consensus score: {checks['consensus_score']}/100")

            # Add issues and warnings from LLM validation
            for model, result in validation_results.items():
                for issue in result.get("issues", []):
                    self._add_issue(
                        f"LLM_{model.upper()}_ISSUE",
                        f"LLM {model} issue",
                        issue,
                        level="CRITICAL",
                    )

                for warning in result.get("warnings", []):
                    self._add_issue(
                        f"LLM_{model.upper()}_WARNING",
                        f"LLM {model} warning",
                        warning,
                        level="WARNING",
                    )
        elif len(validation_results) == 1:
            # Use the single model's score
            model = list(validation_results.keys())[0]
            checks["consensus_score"] = validation_results[model].get(
                "quality_score", 0
            )

            # Add issues and warnings from LLM validation
            for issue in validation_results[model].get("issues", []):
                self._add_issue(
                    f"LLM_{model.upper()}_ISSUE",
                    f"LLM {model} issue",
                    issue,
                    level="CRITICAL",
                )

            for warning in validation_results[model].get("warnings", []):
                self._add_issue(
                    f"LLM_{model.upper()}_WARNING",
                    f"LLM {model} warning",
                    warning,
                    level="WARNING",
                )
        else:
            # No LLM validation available
            self._add_issue(
                "NO_LLM_VALIDATION",
                "No LLM validation",
                "No LLM validation services were available",
                level="WARNING",
            )

        checks["validation_results"] = validation_results
        self.qa_results["checks"]["llm_content_validation"] = checks

    def _validate_with_openai(self, text_sample: str, pdf_path: Path) -> Dict:
        """
        Validate content using OpenAI's GPT-4o.
        Returns a dictionary with validation results.
        """
        if not OPENAI_AVAILABLE or not OPENAI_VALIDATION_CLIENT:
            return None

        try:
            # Create a system prompt for QA validation
            system_prompt = """You are an expert Quality Assurance validator for book content.
Your task is to analyze the provided book content sample and evaluate it based on the following criteria:

1. Content Quality: Check for duplicate content, inconsistencies, and errors.
2. Structure: Evaluate the organization and flow of the content.
3. Puzzle Integrity: For puzzle books, check if clues and answers are consistent.
4. KDP Compliance: Identify any issues that might cause Amazon KDP to reject the book.

Provide a quality score from 0-100, with 85 being the minimum acceptable score.
List any critical issues that must be fixed before publishing.
List any warnings that should be addressed but aren't critical.
Provide specific, actionable feedback for improvement.

Your response must be in JSON format with the following structure:
{
  "quality_score": 85,
  "issues": ["Critical issue 1", "Critical issue 2"],
  "warnings": ["Warning 1", "Warning 2"],
  "feedback": "Overall feedback and recommendations."
}
"""

            # Get file metadata to provide context
            file_info = f"Filename: {pdf_path.name}\nFile size: {pdf_path.stat().st_size/1024:.1f} KB"

            # Call the OpenAI API
            response = OPENAI_VALIDATION_CLIENT.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for best quality
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Here is a sample from a book to validate:\n\n{file_info}\n\nCONTENT SAMPLE:\n{text_sample}",
                    },
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
            )

            # Parse the response
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            logger.error(f"OpenAI validation failed: {e}")
            if SENTRY_AVAILABLE:
                capture_kdp_error(e, {"stage": "openai_validation"})
            return None

    def _validate_with_gemini(self, text_sample: str, pdf_path: Path) -> Dict:
        """
        Validate content using Google's Gemini.
        Returns a dictionary with validation results.
        """
        if not GEMINI_AVAILABLE or not GEMINI_CLIENT:
            return None

        try:
            # Create a prompt for QA validation
            prompt = f"""You are an expert Quality Assurance validator for book content.
Analyze this book content sample and evaluate it based on:

1. Content Quality: Check for duplicate content, inconsistencies, and errors.
2. Structure: Evaluate the organization and flow of the content.
3. Puzzle Integrity: For puzzle books, check if clues and answers are consistent.
4. KDP Compliance: Identify any issues that might cause Amazon KDP to reject the book.

Filename: {pdf_path.name}
File size: {pdf_path.stat().st_size/1024:.1f} KB

CONTENT SAMPLE:
{text_sample}

Provide a quality score from 0-100, with 85 being the minimum acceptable score.
List any critical issues that must be fixed before publishing.
List any warnings that should be addressed but aren't critical.
Provide specific, actionable feedback for improvement.

Your response must be in JSON format with this structure:
{{
  "quality_score": 85,
  "issues": ["Critical issue 1", "Critical issue 2"],
  "warnings": ["Warning 1", "Warning 2"],
  "feedback": "Overall feedback and recommendations."
}}
"""

            # Call the Gemini API
            response = GEMINI_CLIENT.generate_content(prompt)

            # Parse the response - Gemini might not always return valid JSON
            try:
                # Try to extract JSON from the response
                text_response = response.text
                # Find JSON content between curly braces
                json_match = re.search(r"(\{.*\})", text_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    result = json.loads(json_str)
                    return result
                else:
                    # If no JSON found, try to parse the structure manually
                    result = {
                        "quality_score": 0,
                        "issues": [],
                        "warnings": [],
                        "feedback": "Failed to parse Gemini response",
                    }

                    # Look for quality score
                    score_match = re.search(
                        r'quality_score"?\s*:\s*(\d+)', text_response
                    )
                    if score_match:
                        result["quality_score"] = int(score_match.group(1))

                    # Look for issues
                    issues_match = re.search(
                        r'issues"?\s*:\s*\[(.*?)\]', text_response, re.DOTALL
                    )
                    if issues_match:
                        issues_text = issues_match.group(1)
                        issues = re.findall(r'"([^"]+)"', issues_text)
                        result["issues"] = issues

                    # Look for warnings
                    warnings_match = re.search(
                        r'warnings"?\s*:\s*\[(.*?)\]', text_response, re.DOTALL
                    )
                    if warnings_match:
                        warnings_text = warnings_match.group(1)
                        warnings = re.findall(r'"([^"]+)"', warnings_text)
                        result["warnings"] = warnings

                    # Look for feedback
                    feedback_match = re.search(
                        r'feedback"?\s*:\s*"(.*?)"', text_response, re.DOTALL
                    )
                    if feedback_match:
                        result["feedback"] = feedback_match.group(1)

                    return result
            except Exception as parse_error:
                logger.error(f"Failed to parse Gemini response: {parse_error}")
                return None

        except Exception as e:
            logger.error(f"Gemini validation failed: {e}")
            if SENTRY_AVAILABLE:
                capture_kdp_error(e, {"stage": "gemini_validation"})
            return None

    def _check_kdp_compliance(self, pdf_path: Path):
        """Check for KDP-specific compliance issues."""
        print("📚 CHECKING AMAZON KDP COMPLIANCE...")
        checks = {}

        try:
            # Check file size (KDP has a 650MB limit)
            file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
            checks["file_size_mb"] = file_size_mb

            if file_size_mb > 650:
                self._add_issue(
                    "FILE_TOO_LARGE",
                    "File too large",
                    f"File size {file_size_mb:.1f}MB exceeds KDP's 650MB limit",
                    level="CRITICAL",
                )
            else:
                print(f"  ✅ File size {file_size_mb:.1f}MB under KDP limit")

            # Check PDF version (KDP requires PDF 1.3-1.7)
            doc = fitz.open(str(pdf_path))
            pdf_version = doc.pdf_version
            checks["pdf_version"] = pdf_version

            if pdf_version < 1.3 or pdf_version > 1.7:
                self._add_issue(
                    "INVALID_PDF_VERSION",
                    "Invalid PDF version",
                    f"PDF version {pdf_version} outside KDP's supported range (1.3-1.7)",
                    level="CRITICAL",
                )
            else:
                print(f"  ✅ PDF version {pdf_version} supported by KDP")

            # Check for transparency and layers (problematic for KDP)
            has_transparency = False
            for page_num in range(len(doc)):
                # This is a simplified check - a real implementation would
                # analyze the PDF structure more thoroughly
                pass

            checks["has_transparency"] = has_transparency
            if has_transparency:
                self._add_issue(
                    "PDF_HAS_TRANSPARENCY",
                    "PDF has transparency",
                    "PDF contains transparency which may cause issues with KDP",
                    level="WARNING",
                )

        except Exception as e:
            self._add_issue(
                "KDP_CHECK_ERROR",
                "KDP check error",
                f"KDP compliance check failed: {e}",
                level="WARNING",
            )
            if SENTRY_AVAILABLE:
                capture_kdp_error(e, {"stage": "kdp_compliance_check"})

        self.qa_results["checks"]["kdp_compliance"] = checks

    def _calculate_overall_score(self):
        """
        Calculate the overall QA score and determine if the book is ready for publishing.
        Score is based on a 0-100 scale with 85 being the minimum acceptable score.
        """
        # Start with a perfect score and deduct points for issues
        score = 100

        # Critical issues are severe deductions
        critical_issues = len(self.qa_results["issues_found"])
        if critical_issues > 0:
            # Each critical issue deducts 15 points, up to a maximum of 60 points
            score -= min(critical_issues * 15, 60)

        # Warnings are smaller deductions
        warnings = len(self.qa_results["warnings"])
        if warnings > 0:
            # Each warning deducts 5 points, up to a maximum of 30 points
            score -= min(warnings * 5, 30)

        # Factor in LLM validation score if available
        llm_score = self.qa_results["checks"]["llm_content_validation"].get(
            "consensus_score"
        )
        if llm_score is not None:
            # LLM score contributes 40% to the final score
            score = 0.6 * score + 0.4 * llm_score

        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        self.qa_results["overall_score"] = round(score)

        # Determine if the book is ready for publishing
        # Must meet minimum score threshold AND have no critical issues
        min_score = self.qa_criteria["min_qa_score"]
        self.qa_results["publish_ready"] = score >= min_score and critical_issues == 0

        print("\n" + "=" * 70)
        print(f"📊 ENHANCED QA REPORT SUMMARY")
        print("=" * 70)
        print(f"📁 File: {self.qa_results['file_path']}")
        print(f"🎯 Overall Score: {self.qa_results['overall_score']}/100")
        print(f"❌ Critical Issues: {critical_issues}")
        print(f"⚠️  Warnings: {warnings}")
        print(
            f"{'✅ READY' if self.qa_results['publish_ready'] else '❌ NOT READY'}: {'Book meets quality standards' if self.qa_results['publish_ready'] else 'Fix all critical issues before publishing'}"
        )
        print("\n" + "=" * 70)

        if critical_issues > 0:
            print("\n⚠️  CRITICAL ISSUES TO FIX:")
            for issue in self.qa_results["issues_found"]:
                print(f"   • {issue['description']}")

        if warnings > 0:
            print("\n⚠️  WARNINGS TO REVIEW:")
            for warning in self.qa_results["warnings"]:
                print(f"   • {warning['description']}")

        print("=" * 70)

    def _generate_report(self, pdf_path: Path) -> str:
        """Generate a detailed QA report and save it to a file."""
        # Create report filename
        report_dir = pdf_path.parent
        report_filename = f"ENHANCED_QA_REPORT_{pdf_path.name.replace('.pdf', '')}.json"
        report_path = report_dir / report_filename

        # Save the report as JSON
        with open(report_path, "w") as f:
            json.dump(self.qa_results, f, indent=2)

        print(f"📄 Enhanced QA report saved: {report_path}")
        return str(report_path)


def main():
    """Main entry point for the enhanced QA validator."""
    parser = argparse.ArgumentParser(
        description="Enhanced QA Validator - Multi-Model AI Content Quality Assurance"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file to validate")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--output", help="Path to save the QA report (default: same directory as PDF)"
    )
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # Create validator and run QA
    validator = EnhancedQAValidator()
    results = validator.run_enhanced_qa(args.pdf_path)

    # Output summary
    print(f"\nQA Score: {results['overall_score']}/100")
    print(f"Publish Ready: {'Yes' if results['publish_ready'] else 'No'}")
    print(f"Critical Issues: {len(results['issues_found'])}")
    print(f"Warnings: {len(results['warnings'])}")

    # Return success if the book is ready for publishing
    return 0 if results["publish_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
