#!/usr/bin/env python3
"""
Batch Processor for KindleMint Engine
Orchestrates the entire book generation workflow with resume capability
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
import importlib.util
import shutil
# Make Path alias available *before* load_dotenv so it's usable in the path expression
from pathlib import Path as _PathForSentry
# --------------------------------------------------------------------------- #
# Load environment variables early so Sentry / Slack see them
# --------------------------------------------------------------------------- #
from dotenv import load_dotenv

# Load .env file from repository root (one directory above this script)
# `override=False` keeps already-set env vars (e.g. GitHub Actions secrets).
load_dotenv(dotenv_path=(_PathForSentry(__file__).parent.parent / ".env"), override=False)

# --- Sentry integration ------------------------------------------------------

# Ensure we can import `sentry_config` that lives in the *scripts* folder even
# when this file is executed from repository root.
_SCRIPTS_DIR = (_PathForSentry(__file__).parent / "scripts").resolve()
if _SCRIPTS_DIR.exists() and str(_SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(_SCRIPTS_DIR))

try:
    from sentry_config import init_sentry, add_breadcrumb, capture_kdp_error
except Exception:  # pragma: no cover – fallback stubs if Sentry not available

    def init_sentry(*_, **__):
        return False

    def add_breadcrumb(*_, **__):
        pass

    def capture_kdp_error(*_, **__):
        pass

# --- Slack integration -------------------------------------------------------
try:
    from slack_notifier import SlackNotifier
    SLACK_AVAILABLE = True
except Exception:  # pragma: no cover – fallback if Slack notifier not available
    SLACK_AVAILABLE = False
    
    class SlackNotifier:
        """Stub SlackNotifier when module not available"""
        def __init__(self, *args, **kwargs):
            self.enabled = False
        
        def send_message(self, *args, **kwargs):
            return False
        
        def send_batch_complete(self, *args, **kwargs):
            return False
        
        def send_error(self, *args, **kwargs):
            return False
        
        def send_book_complete(self, *args, **kwargs):
            return False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("batch_processor.log")
    ]
)
logger = logging.getLogger("BatchProcessor")

class BatchProcessor:
    """Orchestrates the entire book generation workflow"""
    
    def __init__(self, config_path: str, resume_file: Optional[str] = None):
        """Initialize the batch processor with configuration"""
        self.config_path = Path(config_path)
        self.resume_file = resume_file
        self.config = self._load_config()
        self.batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "batch_id": self.batch_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "books_processed": 0,
            "books_succeeded": 0,
            "books_failed": 0,
            "total_time_seconds": 0,
            "book_results": {}
        }
        self.progress_state = self._load_progress() if resume_file else {}
        
        # Create batch report directory
        self.report_dir = Path(f"batch_reports/{self.batch_id}")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup console progress indicators
        self.step_indicators = {
            "init": "🚀",
            "crossword": "🔤",
            "pdf": "📄",
            "epub": "📱",
            "hardcover": "📚",
            "qa": "✅",
            "complete": "🎉",
            "failed": "❌"
        }

        # Initialise Sentry (no-op if DSN not provided)
        self.sentry_enabled = init_sentry("batch_processor")
        if self.sentry_enabled:
            add_breadcrumb("BatchProcessor initialised", category="initialisation")
        
        # Initialize Slack notifier
        self.slack_notifier = SlackNotifier()
        self.slack_enabled = self.slack_notifier.enabled
        
        # Check if individual book notifications are enabled
        self.notify_on_book_complete = os.getenv('SLACK_NOTIFY_PER_BOOK', 'false').lower() == 'true'
        
        if self.slack_enabled:
            logger.info("Slack notifications enabled for batch processing")
            if self.notify_on_book_complete:
                logger.info("Individual book completion notifications enabled")
            if self.sentry_enabled:
                add_breadcrumb(
                    "Slack notifier initialized", 
                    category="notification",
                    data={
                        "enabled": self.slack_enabled,
                        "per_book": self.notify_on_book_complete
                    }
                )
    
    def _load_config(self) -> Dict:
        """Load batch configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
    
    def _load_progress(self) -> Dict:
        """Load progress state from resume file"""
        try:
            with open(self.resume_file, 'r') as f:
                progress = json.load(f)
            
            logger.info(f"Resuming from progress file: {self.resume_file}")
            logger.info(f"Found {len(progress.get('book_results', {}))} books with saved progress")
            return progress
        except Exception as e:
            logger.error(f"Failed to load progress file: {e}")
            return {}
    
    def _save_progress(self):
        """Save current progress for potential resume"""
        progress_file = self.report_dir / "batch_progress.json"
        with open(progress_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Progress saved to {progress_file}")
    
    def _import_module_from_path(self, module_path: str, module_name: str):
        """Dynamically import a module from file path"""
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.error(f"Failed to import module {module_name} from {module_path}: {e}")
            return None
    
    def process_batch(self):
        """Process all books in the batch configuration"""
        start_time = time.time()
        total_books = len(self.config["books"])
        
        logger.info(f"Starting batch processing of {total_books} books")
        logger.info(f"Batch ID: {self.batch_id}")
        if self.sentry_enabled:
            add_breadcrumb(
                f"Starting batch of {total_books} books",
                category="batch",
                data={"batch_id": self.batch_id, "total": total_books},
            )
        
        # Process each book
        for i, book_config in enumerate(self.config["books"]):
            book_id = book_config.get("id", f"book_{i+1}")
            
            # Check if we should skip this book (already processed in resume)
            if self.resume_file and book_id in self.progress_state.get("book_results", {}) and \
               self.progress_state["book_results"][book_id].get("status") == "complete":
                logger.info(f"Skipping already completed book: {book_id}")
                self.results["book_results"][book_id] = self.progress_state["book_results"][book_id]
                self.results["books_processed"] += 1
                self.results["books_succeeded"] += 1
                continue
            
            # Process this book
            logger.info(f"Processing book {i+1}/{total_books}: {book_id}")
            print(f"\n{self.step_indicators['init']} STARTING BOOK: {book_config.get('title', book_id)} ({i+1}/{total_books})")
            
            book_result = self.process_book(book_config)
            
            # Update batch results
            self.results["book_results"][book_id] = book_result
            self.results["books_processed"] += 1
            
            if book_result["status"] == "complete":
                self.results["books_succeeded"] += 1
                print(f"{self.step_indicators['complete']} BOOK COMPLETE: {book_config.get('title', book_id)}")
            else:
                self.results["books_failed"] += 1
                print(f"{self.step_indicators['failed']} BOOK FAILED: {book_config.get('title', book_id)}")
            
            # Save progress after each book
            self._save_progress()
            
            # Optional delay between books
            if i < total_books - 1 and self.config.get("delay_between_books", 0) > 0:
                delay = self.config.get("delay_between_books")
                logger.info(f"Waiting {delay} seconds before next book...")
                time.sleep(delay)
        
        # Finalize results
        end_time = time.time()
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_time_seconds"] = round(end_time - start_time)
        
        # Generate final report
        self.generate_batch_report()
        
        return self.results
    
    def process_book(self, book_config: Dict) -> Dict:
        """Process a single book through the entire workflow"""
        book_id = book_config.get("id", f"book_{datetime.now().strftime('%H%M%S')}")
        book_title = book_config.get("title", book_id)
        
        book_result = {
            "id": book_id,
            "title": book_title,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "steps_completed": [],
            "steps_failed": [],
            "artifacts": {},
            "status": "in_progress",
            "error": None
        }
        
        # Resume from last successful step if applicable
        last_completed_step = None
        if self.resume_file and book_id in self.progress_state.get("book_results", {}):
            last_completed_step = self.progress_state["book_results"][book_id].get("steps_completed", [])[-1] \
                if self.progress_state["book_results"][book_id].get("steps_completed") else None
            
            if last_completed_step:
                logger.info(f"Resuming book {book_id} from step after '{last_completed_step}'")
                book_result["steps_completed"] = self.progress_state["book_results"][book_id]["steps_completed"]
                book_result["artifacts"] = self.progress_state["book_results"][book_id]["artifacts"]
        
        try:
            # Step 1: Generate puzzles (if needed)
            if "generate_puzzles" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="generate_puzzles",
                    display_name="Generating puzzles",
                    emoji=self.step_indicators["crossword"],
                    book_config=book_config,
                    book_result=book_result
                )
            
            # Step 2: Create PDF interior
            if "create_pdf" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="create_pdf",
                    display_name="Creating PDF interior",
                    emoji=self.step_indicators["pdf"],
                    book_config=book_config,
                    book_result=book_result
                )
            
            # Step 3: Generate EPUB (if enabled)
            if book_config.get("create_epub", True) and "create_epub" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="create_epub",
                    display_name="Generating EPUB",
                    emoji=self.step_indicators["epub"],
                    book_config=book_config,
                    book_result=book_result
                )
            
            # Step 4: Create hardcover package (if enabled)
            if book_config.get("create_hardcover", True) and "create_hardcover" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="create_hardcover",
                    display_name="Creating hardcover package",
                    emoji=self.step_indicators["hardcover"],
                    book_config=book_config,
                    book_result=book_result
                )
            
            # Step 5: Run QA checks
            if "run_qa" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="run_qa",
                    display_name="Running QA checks",
                    emoji=self.step_indicators["qa"],
                    book_config=book_config,
                    book_result=book_result
                )
            
            # All steps completed successfully
            book_result["status"] = "complete"
            logger.info(f"Book {book_id} processed successfully")
            
            # ------------------------------------------------------------------
            # Business Metrics: basic profit / cost estimates
            # ------------------------------------------------------------------
            # Very simple model:
            #   cost_estimate  : printing_cost_estimate from config (default 0)
            #   price_estimate : prefer kindle_price if EPUB enabled
            #                    else hardcover_price_max if hardcover enabled
            #                    else 0
            #   profit_estimate: price_estimate - cost_estimate  (min 0)
            # These numbers can be refined later; they give Slack an immediate
            # sense of business impact.
            cost_estimate = float(book_config.get("printing_cost_estimate", 0) or 0)
            price_estimate = 0.0
            if book_config.get("create_epub", True):
                price_estimate = float(book_config.get("kindle_price", 0) or 0)
            elif book_config.get("create_hardcover", True):
                price_estimate = float(book_config.get("hardcover_price_max", 0) or 0)

            # Do NOT clamp to zero – negative profit highlights unprofitable books
            profit_estimate = round(price_estimate - cost_estimate, 2)

            book_result["cost_estimate"] = round(cost_estimate, 2)
            book_result["price_estimate"] = round(price_estimate, 2)
            book_result["profit_estimate"] = round(profit_estimate, 2)

            # ------------------------------------------------------------------
            # Quality metrics: bubble up QA score & KDP readiness to top-level
            # ------------------------------------------------------------------
            if "qa_score" in book_result["artifacts"]:
                book_result["qa_score"] = book_result["artifacts"]["qa_score"]

            if "publish_ready" in book_result["artifacts"]:
                book_result["publish_ready"] = book_result["artifacts"]["publish_ready"]
            # ------------------------------------------------------------------
        except Exception as e:
            # Record the failure
            error_msg = str(e)
            logger.error(f"Error processing book {book_id}: {error_msg}")
            logger.error(traceback.format_exc())
            
            book_result["status"] = "failed"
            book_result["error"] = error_msg
            # Ensure business keys exist to avoid KeyError in aggregation
            book_result.setdefault("cost_estimate", 0.0)
            book_result.setdefault("price_estimate", 0.0)
            book_result.setdefault("profit_estimate", 0.0)
            # Send Slack notification for critical error
            if self.slack_enabled:
                try:
                    logger.info(f"Sending error notification to Slack for book {book_id}")
                    if self.sentry_enabled:
                        add_breadcrumb(
                            "Sending book error to Slack",
                            category="notification",
                            data={"book_id": book_id, "error": error_msg[:100]}
                        )
                    
                    context = {
                        "book_id": book_id,
                        "book_title": book_title,
                        "batch_id": self.batch_id,
                        "steps_completed": len(book_result.get("steps_completed", [])),
                        "last_step": book_result.get("steps_completed", ["none"])[-1] if book_result.get("steps_completed") else "none"
                    }
                    
                    notification_sent = self.slack_notifier.send_error(
                        message=f"Book processing failed: {book_title}",
                        error=e,
                        context=context
                    )
                    
                    if notification_sent:
                        logger.info("Error notification sent to Slack successfully")
                    else:
                        logger.warning("Failed to send error notification to Slack")
                        
                except Exception as slack_error:
                    logger.error(f"Error sending Slack notification: {slack_error}")
                    if self.sentry_enabled:
                        capture_kdp_error(slack_error, {"operation": "slack_error_notification"})
        
        # Finalize book result
        book_result["end_time"] = datetime.now().isoformat()
        
        # Save individual book report
        book_report_path = self.report_dir / f"book_{book_id}.json"
        with open(book_report_path, 'w') as f:
            json.dump(book_result, f, indent=2)
        
        # Send individual book completion notification if enabled
        if self.slack_enabled and self.notify_on_book_complete:
            try:
                logger.info(f"Sending book completion notification to Slack for {book_id}")
                if self.sentry_enabled:
                    add_breadcrumb(
                        "Sending book completion to Slack",
                        category="notification",
                        data={
                            "book_id": book_id, 
                            "status": book_result["status"]
                        }
                    )
                
                notification_sent = self.slack_notifier.send_book_complete(book_result)
                if notification_sent:
                    logger.info("Book completion notification sent to Slack successfully")
                else:
                    logger.warning("Failed to send book completion notification to Slack")
                    
            except Exception as slack_error:
                logger.error(f"Error sending Slack notification: {slack_error}")
                if self.sentry_enabled:
                    capture_kdp_error(slack_error, {"operation": "slack_book_notification"})
        
        return book_result
    
    def _run_step(self, step_name: str, display_name: str, emoji: str, 
                 book_config: Dict, book_result: Dict) -> None:
        """Run a single step in the book generation process"""
        logger.info(f"Running step: {step_name} for book {book_result['id']}")
        print(f"{emoji} {display_name}...")
        
        step_start = time.time()
        
        try:
            # Call the appropriate method based on step name
            method_name = f"_step_{step_name}"
            if hasattr(self, method_name) and callable(getattr(self, method_name)):
                artifacts = getattr(self, method_name)(book_config, book_result)
                if artifacts:
                    book_result["artifacts"].update(artifacts)
            else:
                raise ValueError(f"Step method not implemented: {method_name}")
            
            # Record successful completion
            book_result["steps_completed"].append(step_name)
            logger.info(f"Step {step_name} completed in {time.time() - step_start:.1f}s")
            
        except Exception as e:
            # Record the failure
            book_result["steps_failed"].append(step_name)
            error_msg = f"Step {step_name} failed: {str(e)}"
            logger.error(error_msg)
# -------- Sentry capture on step failure -------------------
            if self.sentry_enabled:
                capture_kdp_error(
                    e,
                    {
                        "book_id": book_result["id"],
                        "step": step_name,
                        "display": display_name,
                    },
                )
            logger.error(traceback.format_exc())
            raise RuntimeError(error_msg)
    
    def _step_generate_puzzles(self, book_config: Dict, book_result: Dict) -> Dict:
        """Generate puzzles for the book"""
        # Determine which script to use based on puzzle type
        puzzle_type = book_config.get("puzzle_type", "crossword")
        
        if puzzle_type == "crossword":
            script_path = Path("scripts/crossword_engine_v2.py")
        elif puzzle_type == "sudoku":
            script_path = Path("scripts/sudoku_generator.py")
        elif puzzle_type == "word_search":
            script_path = Path("scripts/word_search_generator.py")
        else:
            raise ValueError(f"Unsupported puzzle type: {puzzle_type}")
        
        if not script_path.exists():
            raise FileNotFoundError(f"Puzzle generator script not found: {script_path}")
        
        # Prepare output directory
        series_name = book_config.get("series_name", "Default_Series")
        volume = book_config.get("volume", 1)
        output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/puzzles")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run the puzzle generator script
        cmd = [
            sys.executable, 
            str(script_path),
            "--output", str(output_dir),
            "--count", str(book_config.get("puzzle_count", 50)),
            "--difficulty", book_config.get("difficulty", "mixed")
        ]
        
        # Add any additional parameters from book config
        if "puzzle_params" in book_config:
            for key, value in book_config["puzzle_params"].items():
                # CLI flags use kebab-case; convert snake_case keys to kebab-case
                cli_flag = key.replace("_", "-")
                cmd.extend([f"--{cli_flag}", str(value)])
        
        logger.info(f"Running puzzle generator: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Puzzle generation failed: {result.stderr}")
        
        logger.info(f"Puzzle generation output: {result.stdout}")
        
        # Return artifacts
        return {
            "puzzles_dir": str(output_dir),
            "puzzle_count": book_config.get("puzzle_count", 50),
            "puzzle_type": puzzle_type
        }
    
    def _step_create_pdf(self, book_config: Dict, book_result: Dict) -> Dict:
        """Create PDF interior for the book"""
        # Determine which script to use
        script_path = Path("scripts/book_layout_bot.py")
        
        if not script_path.exists():
            raise FileNotFoundError(f"PDF layout script not found: {script_path}")
        
        # Prepare output directory
        series_name = book_config.get("series_name", "Default_Series")
        volume = book_config.get("volume", 1)
        output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/paperback")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run the PDF layout script
        cmd = [
            sys.executable, 
            str(script_path),
            "--input", book_result["artifacts"].get("puzzles_dir", f"books/active_production/{series_name}/volume_{volume}/puzzles"),
            "--output", str(output_dir),
            "--title", book_config.get("title", f"{series_name} Volume {volume}"),
            "--author", book_config.get("author", "Crossword Masters Publishing")
        ]
        
        # Add any additional parameters from book config
        if "pdf_params" in book_config:
            for key, value in book_config["pdf_params"].items():
                cli_flag = key.replace("_", "-")
                # Boolean flags should be added only when True (CLI style `--flag`)
                if isinstance(value, bool):
                    if value:            # True  -> include flag without value
                        cmd.append(f"--{cli_flag}")
                    else:                # False -> omit flag entirely
                        continue
                else:
                    cmd.extend([f"--{cli_flag}", str(value)])
        
        logger.info(f"Running PDF layout: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"PDF layout failed: {result.stderr}")
        
        logger.info(f"PDF layout output: {result.stdout}")
        
        # Find the generated PDF file
        pdf_files = list(output_dir.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in {output_dir}")
        
        interior_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
        
        # Return artifacts
        return {
            "pdf_dir": str(output_dir),
            "interior_pdf": str(interior_pdf)
        }
    
    def _step_create_epub(self, book_config: Dict, book_result: Dict) -> Dict:
        """Generate EPUB for the book"""
        try:
            # Import the EPUB generator module
            epub_module_path = "scripts/enhanced_epub_generator.py"
            epub_module = self._import_module_from_path(epub_module_path, "enhanced_epub_generator")
            
            if not epub_module:
                raise ImportError(f"Could not import EPUB generator from {epub_module_path}")
            
            # Prepare output directory
            series_name = book_config.get("series_name", "Default_Series")
            volume = book_config.get("volume", 1)
            output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/kindle")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a custom EPUB generator instance
            class CustomEpubGenerator(epub_module.EnhancedKindleEpubGenerator):
                def __init__(self, output_dir, book_config):
                    super().__init__()
                    self.output_dir = output_dir
                    self.epub_dir = output_dir / "epub_enhanced_build"
                    self.epub_dir.mkdir(parents=True, exist_ok=True)
                    self.book_config = book_config
            
            # Generate the EPUB
            generator = CustomEpubGenerator(output_dir, book_config)
            epub_file = generator.create_enhanced_epub()
            
            # Create metadata file
            metadata = {
                "title": book_config.get("title", f"{series_name} Volume {volume}"),
                "author": book_config.get("author", "Crossword Masters Publishing"),
                "description": book_config.get("description", "A collection of puzzles"),
                "keywords": book_config.get("keywords", ["puzzles", "crossword"]),
                "language": book_config.get("language", "en"),
                "publication_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            metadata_file = output_dir / "kindle_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create publishing checklist
            checklist = f"""# Kindle Publishing Checklist
## {book_config.get("title", f"{series_name} Volume {volume}")}

### 📊 **EPUB Specifications**
- **Format**: EPUB 3.0
- **File Size**: {os.path.getsize(epub_file) / (1024*1024):.2f} MB
- **Enhanced Features**: Navigation, high-res grids, marketing back-matter

### 📋 **Publishing Steps**
1. [ ] Log into KDP Dashboard
2. [ ] Create new Kindle eBook
3. [ ] Enter book details from metadata.json
4. [ ] Upload EPUB file
5. [ ] Set pricing and royalty options
6. [ ] Submit for review

### 💰 **Pricing Strategy**
- **Recommended Price**: ${book_config.get("kindle_price", 2.99)}
- **Royalty Option**: 70%

### 📈 **Marketing Notes**
- Include "Large Print" in keywords
- Set primary category to Games & Puzzles
- Enable Kindle Unlimited if possible
"""
            
            checklist_file = output_dir / "kindle_publishing_checklist.md"
            with open(checklist_file, 'w') as f:
                f.write(checklist)
            
            # Return artifacts
            return {
                "epub_dir": str(output_dir),
                "epub_file": str(epub_file),
                "kindle_metadata": str(metadata_file),
                "kindle_checklist": str(checklist_file)
            }
            
        except Exception as e:
            logger.error(f"EPUB generation failed: {e}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"EPUB generation failed: {str(e)}")
    
    def _step_create_hardcover(self, book_config: Dict, book_result: Dict) -> Dict:
        """Create hardcover package for the book"""
        try:
            # Prepare hardcover config
            series_name = book_config.get("series_name", "Default_Series")
            volume = book_config.get("volume", 1)
            
            # Create hardcover directory
            output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/hardcover")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the interior PDF to hardcover directory (per File Organization Policy)
            interior_pdf_path = book_result["artifacts"].get("interior_pdf")
            if interior_pdf_path and Path(interior_pdf_path).exists():
                hardcover_interior_pdf = output_dir / Path(interior_pdf_path).name
                shutil.copy2(interior_pdf_path, hardcover_interior_pdf)
                logger.info(f"Copied interior PDF to hardcover directory: {hardcover_interior_pdf}")
            
            # Create hardcover config file
            hardcover_config = {
                "title": book_config.get("title", f"{series_name} Volume {volume}"),
                "subtitle": book_config.get("subtitle", "50 Puzzles for Relaxation"),
                "author": book_config.get("author", "Crossword Masters Publishing"),
                "publisher": book_config.get("publisher", "Crossword Masters Publishing"),
                "description": book_config.get("description", "A collection of puzzles"),
                "keywords": book_config.get("keywords", ["puzzles", "crossword", "hardcover"]),
                "categories": book_config.get("categories", ["Games & Puzzles"]),
                "language": book_config.get("language", "en"),
                "pages": book_config.get("pages", 110),
                "hardcover_price_min": book_config.get("hardcover_price_min", 14.99),
                "hardcover_price_max": book_config.get("hardcover_price_max", 19.99),
                "target_audience": book_config.get("target_audience", "Puzzle enthusiasts"),
                "printing_cost_estimate": book_config.get("printing_cost_estimate", 5.50),
                "royalty_min": book_config.get("hardcover_royalty_min", 4.50),
                "royalty_max": book_config.get("hardcover_royalty_max", 7.50),
                "cover_source": book_result["artifacts"].get("cover_image", "default_cover.jpg"),
                "output_dir": str(output_dir),
                "back_cover_description": book_config.get("back_cover_description", 
                                                        "Enjoy these carefully crafted puzzles\nDesigned for hours of entertainment\nPerfect gift for puzzle enthusiasts")
            }
            
            hardcover_config_file = output_dir / "hardcover_config.json"
            with open(hardcover_config_file, 'w') as f:
                json.dump(hardcover_config, f, indent=2)
            
            # Run hardcover package script
            cmd = [
                sys.executable,
                "scripts/hardcover/create_hardcover_package.py",
                str(hardcover_config_file)
            ]
            
            logger.info(f"Running hardcover package creation: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Hardcover package creation failed: {result.stderr}")
            
            logger.info(f"Hardcover package output: {result.stdout}")
            
            # Return artifacts
            return {
                "hardcover_dir": str(output_dir),
                "hardcover_config": str(hardcover_config_file),
                "hardcover_checklist": str(output_dir / "hardcover_production_checklist.md"),
                "hardcover_metadata": str(output_dir / "amazon_kdp_metadata.json"),
                "hardcover_interior_pdf": str(hardcover_interior_pdf) if 'hardcover_interior_pdf' in locals() else None
            }
            
        except Exception as e:
            logger.error(f"Hardcover package creation failed: {e}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Hardcover package creation failed: {str(e)}")
    
    def _step_run_qa(self, book_config: Dict, book_result: Dict) -> Dict:
        """Run QA checks on the generated files"""
        try:
            # Import the new QA validation pipeline
            qa_module_path = "scripts/qa_validation_pipeline.py"
            qa_module = self._import_module_from_path(qa_module_path, "qa_validation_pipeline")
            
            if not qa_module:
                raise ImportError(f"Could not import QA validation pipeline from {qa_module_path}")
            
            # Import the artifacts interface
            artifacts_module_path = "scripts/qa_artifacts_interface.py"
            artifacts_module = self._import_module_from_path(artifacts_module_path, "qa_artifacts_interface")
            
            # Get the interior PDF path
            interior_pdf = book_result["artifacts"].get("interior_pdf")
            if not interior_pdf:
                raise ValueError("Interior PDF not found in artifacts")
            
            # Run QA validation
            pipeline = qa_module.QAValidationPipeline()
            book_type = book_config.get("puzzle_type", "crossword")
            qa_result = pipeline.validate_pdf(Path(interior_pdf), book_type=book_type)
            
            # Save QA results
            series_name = book_config.get("series_name", "Default_Series")
            volume = book_config.get("volume", 1)
            output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/qa")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert QAResult dataclass to dict for JSON serialization
            qa_results_dict = qa_module.asdict(qa_result)
            
            qa_report_file = output_dir / f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(qa_report_file, 'w') as f:
                json.dump(qa_results_dict, f, indent=2)
            
            # Generate Claude Artifacts interface if available
            qa_artifact_file = None
            if artifacts_module:
                interface = artifacts_module.QAArtifactsInterface()
                html = interface.generate_qa_artifact(qa_results_dict, Path(interior_pdf))
                qa_artifact_file = output_dir / f"qa_artifact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                interface.save_artifact(html, qa_artifact_file)
                
                # Also generate markdown summary
                markdown_summary = interface.generate_markdown_summary(qa_results_dict)
                summary_file = output_dir / "qa_summary.md"
                with open(summary_file, 'w') as f:
                    f.write(markdown_summary)
            
            # Create validation report
            validation_report = f"""# Quality Assurance Report
## {book_config.get("title", f"{series_name} Volume {volume}")}

### 📊 **QA Results**
- **Overall Score**: {qa_result.overall_score}/100
- **Status**: {'✅ PASSED' if qa_result.passed else '❌ FAILED'}
- **Validation Model**: {qa_result.validation_model}
- **Timestamp**: {qa_result.timestamp}

### 📋 **Criteria Breakdown**
"""
            
            for criterion, details in qa_result.criteria.items():
                status = "✅" if details.get("passed", False) else "❌"
                validation_report += f"- {status} **{criterion}**: {details['score']} (threshold: {details['threshold']})\n"
            
            if qa_result.issues_found:
                validation_report += f"\n### ⚠️ **Issues Found** ({len(qa_result.issues_found)})\n"
                for issue in qa_result.issues_found[:10]:
                    validation_report += f"- {issue.get('type', 'Unknown')}: {issue.get('message', str(issue))}\n"
            
            if qa_result.recommendations:
                validation_report += f"\n### 💡 **Recommendations**\n"
                for rec in qa_result.recommendations:
                    validation_report += f"- {rec}\n"
            
            validation_report += f"\n### 📋 **Next Steps**\n"
            validation_report += '✅ Book is ready for publishing!' if qa_result.passed else '❌ Fix issues before publishing (minimum score: 85/100)'
            
            validation_report_file = output_dir / "qa_validation_report.md"
            with open(validation_report_file, 'w') as f:
                f.write(validation_report)
            
            # Return artifacts
            artifacts = {
                "qa_dir": str(output_dir),
                "qa_report": str(qa_report_file),
                "validation_report": str(validation_report_file),
                "publish_ready": qa_result.passed,
                "qa_score": qa_result.overall_score
            }
            
            if qa_artifact_file:
                artifacts["qa_artifact"] = str(qa_artifact_file)
            
            return artifacts
            
        except Exception as e:
            logger.error(f"QA check failed: {e}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"QA check failed: {str(e)}")
    
    def generate_batch_report(self) -> str:
        """Generate a comprehensive batch report"""
        # Calculate statistics
        total_time = self.results["total_time_seconds"]
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        seconds = total_time % 60
        
        books_processed = self.results["books_processed"]
        books_succeeded = self.results["books_succeeded"]
        books_failed = self.results["books_failed"]
        success_rate = (books_succeeded / books_processed * 100) if books_processed > 0 else 0
        # ------------------------------------------------------------------ #
        # 1. Aggregate business metrics from individual book results
        # ------------------------------------------------------------------ #
        total_profit: float = 0.0
        total_cost:   float = 0.0
        qa_scores:    List[int] = []
        kdp_ready_count: int = 0

        for _bid, bres in self.results["book_results"].items():
            total_profit += float(bres.get("profit_estimate", 0) or 0)
            total_cost   += float(bres.get("cost_estimate",   0) or 0)
            if "qa_score" in bres and isinstance(bres["qa_score"], (int, float)):
                qa_scores.append(bres["qa_score"])
            if bres.get("publish_ready"):
                kdp_ready_count += 1

        avg_profit_per_book = (total_profit / books_processed) if books_processed else 0
        avg_qa_score        = (sum(qa_scores) / len(qa_scores)) if qa_scores else None
        cost_per_book       = (total_cost / books_processed) if books_processed else 0
        roi_percentage      = ((total_profit / total_cost) * 100) if total_cost else None
        production_eff      = (total_time / books_processed) if books_processed else None  # secs/book

        # Placeholder for historical comparison (could be filled externally)
        previous_success_rate = None

        # Persist metrics in results so SlackNotifier can use them
        self.results.update({
            "total_profit":           round(total_profit,  2),
            "avg_profit_per_book":    round(avg_profit_per_book, 2),
            "total_cost":             round(total_cost,    2),
            "cost_per_book":          round(cost_per_book, 2),
            "roi_percentage":         round(roi_percentage, 2) if roi_percentage is not None else None,
            "avg_qa_score":           round(avg_qa_score, 1) if avg_qa_score is not None else None,
            "production_efficiency":  round(production_eff, 2) if production_eff is not None else None,
            "kdp_ready_count":        kdp_ready_count,
            "previous_success_rate":  previous_success_rate
        })
        
        # Create summary report
        summary = f"""# KindleMint Engine Batch Processing Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Batch ID: {self.batch_id}

## 📊 Summary
- **Books Processed**: {books_processed}
- **Successful**: {books_succeeded}
- **Failed**: {books_failed}
- **Success Rate**: {success_rate:.1f}%
- **Total Time**: {hours:02d}:{minutes:02d}:{seconds:02d}

## 📚 Book Details
"""
        
        # Add details for each book
        for book_id, book_result in self.results["book_results"].items():
            book_time = 0
            if book_result.get("start_time") and book_result.get("end_time"):
                start = datetime.fromisoformat(book_result["start_time"])
                end = datetime.fromisoformat(book_result["end_time"])
                book_time = (end - start).total_seconds()
            
            book_minutes = int(book_time // 60)
            book_seconds = int(book_time % 60)
            
            summary += f"""
### {book_result.get('title', book_id)}
- **Status**: {'✅ Complete' if book_result.get('status') == 'complete' else '❌ Failed'}
- **Processing Time**: {book_minutes}m {book_seconds}s
- **Steps Completed**: {len(book_result.get('steps_completed', []))}
"""
            
            if book_result.get('status') != 'complete':
                summary += f"- **Error**: {book_result.get('error', 'Unknown error')}\n"
        
        # Add recommendations
        summary += """
## 🚀 Recommendations
- Review any failed books and address errors
- Check QA reports for quality issues
- Verify hardcover cover wraps for proper alignment
- Run batch processor with --resume flag to retry failed books
"""
        
        # Save summary report
        report_file = self.report_dir / "batch_summary.md"
        with open(report_file, 'w') as f:
            f.write(summary)
        
        # Save detailed JSON report
        json_report_file = self.report_dir / "batch_report.json"
        with open(json_report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Batch report generated: {report_file}")
        logger.info(f"Detailed JSON report: {json_report_file}")
        
        # Print summary to console
        print("\n" + "=" * 80)
        print(f"🎯 BATCH PROCESSING COMPLETE: {self.batch_id}")
        print(f"📚 Books: {books_succeeded}/{books_processed} successful ({success_rate:.1f}%)")
        print(f"⏱️ Total time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"📄 Report: {report_file}")
        print("=" * 80)
        
        # Send Slack notification for batch completion
        if self.slack_enabled:
            try:
                logger.info("Sending batch completion notification to Slack")
                if self.sentry_enabled:
                    add_breadcrumb(
                        "Sending batch completion to Slack",
                        category="notification",
                        data={
                            "batch_id": self.batch_id,
                            "success_rate": success_rate
                        }
                    )
                
                notification_sent = self.slack_notifier.send_batch_complete(self.results)
                if notification_sent:
                    logger.info("Batch completion notification sent to Slack successfully")
                else:
                    logger.warning("Failed to send batch completion notification to Slack")
                    
            except Exception as e:
                logger.error(f"Error sending Slack notification: {e}")
                if self.sentry_enabled:
                    capture_kdp_error(e, {"operation": "slack_batch_notification"})
        
        return str(report_file)

def main():
    """Main entry point for batch processor"""
    parser = argparse.ArgumentParser(description='KindleMint Engine Batch Processor')
    parser.add_argument('config', help='Batch configuration JSON file')
    parser.add_argument('--resume', help='Resume from previous progress file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    print("🏭 KINDLEMINT ENGINE BATCH PROCESSOR")
    print("=" * 50)
    print(f"📋 Configuration: {args.config}")
    if args.resume:
        print(f"🔄 Resuming from: {args.resume}")
    print("=" * 50)
    
    try:
        processor = BatchProcessor(args.config, args.resume)
        results = processor.process_batch()
        
        # Return success if all books succeeded
        return 0 if results["books_failed"] == 0 else 1
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        logger.error(traceback.format_exc())
        print(f"\n❌ ERROR: {e}")
        
        # Try to send Slack notification for fatal error
        try:
            notifier = SlackNotifier()
            if notifier.enabled:
                notifier.send_error(
                    message="Fatal error in batch processing",
                    error=e,
                    context={
                        "config_file": args.config,
                        "resume_file": args.resume or "none"
                    }
                )
        except:
            pass  # Don't let notification failure prevent proper exit
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
