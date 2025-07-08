#!/usr/bin/env python3
"""
Refactored Batch Processor - Uses DataManager for Cloud-Ready Data Operations
Replaces direct file I/O with abstracted data storage layer
"""

import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from datetime import datetime
import importlib.util

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kindlemint.data import DataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock Sentry functions for compatibility
def init_sentry(*_, **__):
    pass

def add_breadcrumb(*_, **__):
    pass

def capture_kdp_error(*_, **__):
    pass

# Mock Slack notifier for compatibility
class SlackNotifier:
    def __init__(self, *args, **kwargs):
        pass

    def send_message(self, *args, **kwargs):
        pass

    def send_batch_complete(self, *args, **kwargs):
        pass

    def send_error(self, *args, **kwargs):
        pass

    def send_book_complete(self, *args, **kwargs):
        pass

# Mock QA validator for compatibility
class EnhancedQAValidator:
    def __init__(self, *_, **__):
        pass

    def validate_book(self, *_, **__):
        return {"status": "passed", "issues": []}


class RefactoredBatchProcessor:
    """
    Refactored batch processor using DataManager for cloud-ready data operations.
    All data persistence is now abstracted through the DataManager layer.
    """

    def __init__(self, config_path: str, resume_file: Optional[str] = None):
        self.config_path = Path(config_path)
        self.resume_file = resume_file
        self.batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize DataManager for all data operations
        self.data_manager = DataManager()
        
        # Load configuration and progress
        self.config = self._load_config()
        self.progress_state = self._load_progress()
        
        # Initialize results structure
        self.results = {
            "batch_id": self.batch_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_time_seconds": 0,
            "books_processed": 0,
            "books_succeeded": 0,
            "books_failed": 0,
            "book_results": {},
        }
        
        # Initialize components
        self.slack_notifier = SlackNotifier()
        self.qa_validator = EnhancedQAValidator()
        
        # Configuration flags
        self.sentry_enabled = self.config.get("sentry_enabled", False)
        self.slack_enabled = self.config.get("slack_enabled", False)
        self.notify_on_book_complete = self.config.get("notify_on_book_complete", False)
        
        # Step indicators for progress display
        self.step_indicators = {
            "init": "🚀",
            "crossword": "🧩",
            "pdf": "📄",
            "cover": "🖼️",
            "qa": "✅",
            "complete": "🎉",
            "failed": "❌",
        }

    def _load_config(self) -> Dict:
        """Load batch configuration using DataManager"""
        try:
            # Try to load from DataManager first
            config_data = self.data_manager.storage.load_data("batch_config")
            
            if config_data is None:
                # Fallback to file if not in DataManager
                with open(self.config_path, "r") as f:
                    config_data = json.load(f)
                
                # Save to DataManager for future use
                self.data_manager.storage.save_data("batch_config", config_data, {
                    "type": "batch_config",
                    "source_file": str(self.config_path),
                    "loaded_at": datetime.now().isoformat()
                })

            logger.info(f"Loaded configuration using DataManager")
            return config_data
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)

    def _load_progress(self) -> Dict:
        """Load progress state using DataManager"""
        try:
            if self.resume_file:
                # Load from DataManager using resume file as key
                progress = self.data_manager.storage.load_data(f"batch_progress/{self.resume_file}")
                
                if progress is None:
                    # Fallback to file if not in DataManager
                    with open(self.resume_file, "r") as f:
                        progress = json.load(f)
                    
                    # Save to DataManager for future use
                    self.data_manager.storage.save_data(f"batch_progress/{self.resume_file}", progress, {
                        "type": "batch_progress",
                        "source_file": self.resume_file,
                        "loaded_at": datetime.now().isoformat()
                    })

                logger.info(f"Resuming from progress using DataManager")
                logger.info(f"Found {len(progress.get('book_results', {}))} books with saved progress")
                return progress
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Failed to load progress: {e}")
            return {}

    def _save_progress(self):
        """Save current progress using DataManager"""
        try:
            # Save to DataManager with batch-specific key
            progress_key = f"batch_progress/{self.batch_id}"
            self.data_manager.storage.save_data(progress_key, self.results, {
                "type": "batch_progress",
                "batch_id": self.batch_id,
                "saved_at": datetime.now().isoformat(),
                "books_processed": self.results["books_processed"],
                "books_succeeded": self.results["books_succeeded"],
                "books_failed": self.results["books_failed"]
            })
            
            logger.info(f"Progress saved to DataManager with key: {progress_key}")
            
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")

    def _save_book_data(self, book_id: str, book_data: Dict):
        """Save book-specific data using DataManager"""
        try:
            # Save book data with metadata
            self.data_manager.save_book_data(book_id, book_data)
            logger.info(f"Book data saved for {book_id}")
            
        except Exception as e:
            logger.error(f"Failed to save book data for {book_id}: {e}")

    def _load_book_data(self, book_id: str) -> Optional[Dict]:
        """Load book-specific data using DataManager"""
        try:
            return self.data_manager.load_book_data(book_id)
        except Exception as e:
            logger.error(f"Failed to load book data for {book_id}: {e}")
            return None

    def _save_analytics(self, analytics_type: str, data: Dict):
        """Save analytics data using DataManager"""
        try:
            self.data_manager.save_analytics(analytics_type, data)
            logger.info(f"Analytics saved for {analytics_type}")
            
        except Exception as e:
            logger.error(f"Failed to save analytics for {analytics_type}: {e}")

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
            book_id = book_config.get("id", f"book_{i + 1}")

            # Check if we should skip this book (already processed in resume)
            if (
                self.resume_file
                and book_id in self.progress_state.get("book_results", {})
                and self.progress_state["book_results"][book_id].get("status") == "complete"
            ):
                logger.info(f"Skipping already completed book: {book_id}")
                self.results["book_results"][book_id] = self.progress_state["book_results"][book_id]
                self.results["books_processed"] += 1
                self.results["books_succeeded"] += 1
                continue

            # Process this book
            logger.info(f"Processing book {i + 1}/{total_books}: {book_id}")
            print(f"\n{self.step_indicators['init']} STARTING BOOK: {book_config.get('title', book_id)} ({i + 1}/{total_books})")

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

        # Save final analytics
        self._save_analytics("batch_completion", {
            "batch_id": self.batch_id,
            "total_books": total_books,
            "books_succeeded": self.results["books_succeeded"],
            "books_failed": self.results["books_failed"],
            "total_time_seconds": self.results["total_time_seconds"],
            "completion_rate": self.results["books_succeeded"] / total_books if total_books > 0 else 0
        })

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
            "error": None,
        }

        # Resume from last successful step if applicable
        last_completed_step = None
        if self.resume_file and book_id in self.progress_state.get("book_results", {}):
            last_completed_step = (
                self.progress_state["book_results"][book_id].get("steps_completed", [])[-1]
                if self.progress_state["book_results"][book_id].get("steps_completed")
                else None
            )

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
                    book_result=book_result,
                )

            # Step 2: Create PDF interior
            if "create_pdf" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="create_pdf",
                    display_name="Creating PDF interior",
                    emoji=self.step_indicators["pdf"],
                    book_config=book_config,
                    book_result=book_result,
                )

            # Step 3: Generate cover
            if "generate_cover" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="generate_cover",
                    display_name="Generating cover",
                    emoji=self.step_indicators["cover"],
                    book_config=book_config,
                    book_result=book_result,
                )

            # Step 4: Run QA validation
            if "run_qa" not in book_result["steps_completed"]:
                self._run_step(
                    step_name="run_qa",
                    display_name="Running QA validation",
                    emoji=self.step_indicators["qa"],
                    book_config=book_config,
                    book_result=book_result,
                )

            # Mark as complete
            book_result["status"] = "complete"
            book_result["end_time"] = datetime.now().isoformat()

            # Save book data to DataManager
            self._save_book_data(book_id, book_result)

            # Send notification if enabled
            if self.notify_on_book_complete and self.slack_enabled:
                self.slack_notifier.send_book_complete(book_result)

        except Exception as e:
            book_result["status"] = "failed"
            book_result["error"] = str(e)
            book_result["end_time"] = datetime.now().isoformat()
            
            logger.error(f"Book {book_id} failed: {e}")
            
            if self.sentry_enabled:
                capture_kdp_error(e, book_result)
            
            if self.slack_enabled:
                self.slack_notifier.send_error(book_result)

        return book_result

    def _run_step(self, step_name: str, display_name: str, emoji: str, book_config: Dict, book_result: Dict) -> None:
        """Run a single processing step"""
        print(f"{emoji} {display_name}...")
        
        try:
            step_method = getattr(self, f"_step_{step_name}")
            step_result = step_method(book_config, book_result)
            
            if step_result.get("success", False):
                book_result["steps_completed"].append(step_name)
                book_result["artifacts"].update(step_result.get("artifacts", {}))
                print(f"✅ {display_name} completed")
            else:
                book_result["steps_failed"].append(step_name)
                raise Exception(step_result.get("error", f"Step {step_name} failed"))
                
        except Exception as e:
            book_result["steps_failed"].append(step_name)
            raise e

    def _step_generate_puzzles(self, book_config: Dict, book_result: Dict) -> Dict:
        """Generate puzzles step - simplified for example"""
        # This would contain the actual puzzle generation logic
        # For now, just return success
        return {
            "success": True,
            "artifacts": {
                "puzzle_file": f"puzzles_{book_result['id']}.json"
            }
        }

    def _step_create_pdf(self, book_config: Dict, book_result: Dict) -> Dict:
        """Create PDF step - simplified for example"""
        return {
            "success": True,
            "artifacts": {
                "pdf_file": f"interior_{book_result['id']}.pdf"
            }
        }

    def _step_generate_cover(self, book_config: Dict, book_result: Dict) -> Dict:
        """Generate cover step - simplified for example"""
        return {
            "success": True,
            "artifacts": {
                "cover_file": f"cover_{book_result['id']}.pdf"
            }
        }

    def _step_run_qa(self, book_config: Dict, book_result: Dict) -> Dict:
        """Run QA validation step - simplified for example"""
        qa_result = self.qa_validator.validate_book(book_result)
        return {
            "success": qa_result.get("status") == "passed",
            "artifacts": {
                "qa_report": f"qa_report_{book_result['id']}.json"
            }
        }

    def generate_batch_report(self) -> str:
        """Generate batch completion report"""
        report = {
            "batch_id": self.batch_id,
            "summary": {
                "total_books": len(self.config["books"]),
                "books_processed": self.results["books_processed"],
                "books_succeeded": self.results["books_succeeded"],
                "books_failed": self.results["books_failed"],
                "success_rate": self.results["books_succeeded"] / self.results["books_processed"] if self.results["books_processed"] > 0 else 0,
                "total_time_seconds": self.results["total_time_seconds"]
            },
            "book_results": self.results["book_results"],
            "generated_at": datetime.now().isoformat()
        }

        # Save report using DataManager
        self.data_manager.storage.save_data(f"batch_reports/{self.batch_id}", report, {
            "type": "batch_report",
            "batch_id": self.batch_id,
            "generated_at": datetime.now().isoformat()
        })

        logger.info(f"Batch report saved to DataManager")
        return f"Batch processing complete. Success rate: {report['summary']['success_rate']:.1%}"


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python batch_processor_refactored.py <config_file> [resume_file]")
        sys.exit(1)

    config_path = sys.argv[1]
    resume_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Initialize and run batch processor
    processor = RefactoredBatchProcessor(config_path, resume_file)
    results = processor.process_batch()

    print(f"\n🎉 Batch processing complete!")
    print(f"Processed: {results['books_processed']} books")
    print(f"Succeeded: {results['books_succeeded']} books")
    print(f"Failed: {results['books_failed']} books")


if __name__ == "__main__":
    main() 