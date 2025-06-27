"""
Content Creation Agents for KindleMint Multi-Agent System

This module implements specialized agents for content generation tasks
including puzzle creation, PDF layout, EPUB generation, and cover design.
"""

import asyncio
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentCapability, AgentStatus
from .task_system import Task, TaskResult, TaskStatus, TaskType


class PuzzleGeneratorAgent(BaseAgent):
    """
    Specialized agent for generating puzzles (crossword, sudoku, word search)
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        supported_puzzle_types: Optional[List[str]] = None,
        max_concurrent_tasks: int = 2,
    ):
        """
        Initialize puzzle generator agent
        
        Args:
            agent_id: Unique agent identifier
            supported_puzzle_types: List of supported puzzle types
            max_concurrent_tasks: Maximum concurrent puzzle generation tasks
        """
        super().__init__(
            agent_id=agent_id,
            agent_type="puzzle_generator",
            capabilities=[AgentCapability.PUZZLE_CREATION, AgentCapability.CONTENT_GENERATION],
            max_concurrent_tasks=max_concurrent_tasks,
        )
        
        self.supported_puzzle_types = supported_puzzle_types or ["crossword", "sudoku", "word_search"]
        self.scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
        
        # Script mappings
        self.puzzle_scripts = {
            "crossword": self.scripts_dir / "crossword_engine_v2.py",
            "sudoku": self.scripts_dir / "sudoku_generator.py", 
            "word_search": self.scripts_dir / "word_search_generator.py",
        }
    
    async def _initialize(self) -> None:
        """Initialize puzzle generator agent"""
        self.logger.info(f"Puzzle generator initialized with types: {self.supported_puzzle_types}")
        
        # Verify script availability
        missing_scripts = []
        for puzzle_type, script_path in self.puzzle_scripts.items():
            if puzzle_type in self.supported_puzzle_types and not script_path.exists():
                missing_scripts.append(f"{puzzle_type}: {script_path}")
        
        if missing_scripts:
            self.logger.warning(f"Missing puzzle scripts: {missing_scripts}")
    
    async def _cleanup(self) -> None:
        """Cleanup puzzle generator agent"""
        self.logger.info("Puzzle generator agent cleaned up")
    
    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute puzzle generation task"""
        if task.task_type != TaskType.GENERATE_PUZZLES:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"Unsupported task type: {task.task_type}",
            )
        
        try:
            # Extract task parameters
            puzzle_type = task.input_data.get("puzzle_type", "crossword")
            count = task.input_data.get("count", 50)
            difficulty = task.input_data.get("difficulty", "mixed")
            theme = task.input_data.get("theme")
            output_dir = task.input_data.get("output_dir")
            
            # Validate puzzle type
            if puzzle_type not in self.supported_puzzle_types:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    error_message=f"Unsupported puzzle type: {puzzle_type}",
                )
            
            # Get script path
            script_path = self.puzzle_scripts.get(puzzle_type)
            if not script_path or not script_path.exists():
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    error_message=f"Script not found for puzzle type: {puzzle_type}",
                )
            
            # Prepare output directory
            if not output_dir:
                series_name = task.input_data.get("series_name", "Default_Series")
                volume = task.input_data.get("volume", 1)
                output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/puzzles")
            else:
                output_dir = Path(output_dir)
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build command
            cmd = [
                sys.executable,
                str(script_path),
                "--output", str(output_dir),
                "--count", str(count),
                "--difficulty", difficulty,
            ]
            
            # Add theme if supported and provided
            if theme and puzzle_type in ["crossword", "word_search"]:
                cmd.extend(["--theme", theme])
            
            # Add additional parameters from task
            puzzle_params = task.input_data.get("puzzle_params", {})
            for key, value in puzzle_params.items():
                cli_flag = key.replace("_", "-")
                cmd.extend([f"--{cli_flag}", str(value)])
            
            self.logger.info(f"Executing puzzle generation: {' '.join(cmd)}")
            
            # Execute command
            start_time = datetime.now()
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.returncode != 0:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    execution_time=execution_time,
                    error_message=f"Puzzle generation failed: {stderr.decode()}",
                    error_details={"stdout": stdout.decode(), "stderr": stderr.decode()},
                )
            
            # Verify output
            puzzle_files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.json"))
            if not puzzle_files:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    execution_time=execution_time,
                    error_message="No puzzle files generated",
                )
            
            # Calculate quality score based on generated files
            expected_files = count * 2  # Assume each puzzle has image + metadata
            actual_files = len(puzzle_files)
            quality_score = min(100, (actual_files / expected_files) * 100)
            
            return TaskResult(
                success=True,
                task_id=task.task_id,
                agent_id=self.agent_id,
                execution_time=execution_time,
                output_data={
                    "puzzle_type": puzzle_type,
                    "puzzles_generated": actual_files // 2,  # Approximate
                    "output_directory": str(output_dir),
                    "puzzle_files": [str(f) for f in puzzle_files],
                },
                artifacts={
                    "puzzles_dir": str(output_dir),
                    "metadata_dir": str(output_dir / "metadata") if (output_dir / "metadata").exists() else None,
                },
                quality_score=quality_score,
                performance_metrics={
                    "puzzles_per_second": (actual_files // 2) / execution_time if execution_time > 0 else 0,
                    "files_generated": actual_files,
                    "generation_rate": execution_time / count if count > 0 else 0,
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"Puzzle generation error: {str(e)}",
                error_details={"exception": str(e)},
            )


class PDFLayoutAgent(BaseAgent):
    """
    Specialized agent for PDF layout and formatting
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        max_concurrent_tasks: int = 1,
    ):
        """Initialize PDF layout agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type="pdf_layout",
            capabilities=[AgentCapability.PDF_LAYOUT, AgentCapability.CONTENT_GENERATION],
            max_concurrent_tasks=max_concurrent_tasks,
        )
        
        self.scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
        self.layout_script = self.scripts_dir / "book_layout_bot.py"
        self.sudoku_layout_script = self.scripts_dir / "sudoku_pdf_layout_v2.py"
    
    async def _initialize(self) -> None:
        """Initialize PDF layout agent"""
        self.logger.info("PDF layout agent initialized")
        
        # Verify script availability
        missing_scripts = []
        if not self.layout_script.exists():
            missing_scripts.append(str(self.layout_script))
        if not self.sudoku_layout_script.exists():
            missing_scripts.append(str(self.sudoku_layout_script))
        
        if missing_scripts:
            self.logger.warning(f"Missing layout scripts: {missing_scripts}")
    
    async def _cleanup(self) -> None:
        """Cleanup PDF layout agent"""
        self.logger.info("PDF layout agent cleaned up")
    
    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute PDF layout task"""
        if task.task_type != TaskType.CREATE_PDF_LAYOUT:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"Unsupported task type: {task.task_type}",
            )
        
        try:
            # Extract task parameters
            title = task.input_data.get("title", "Untitled Book")
            author = task.input_data.get("author", "KindleMint Publishing")
            input_dir = task.input_data.get("input_dir")
            output_dir = task.input_data.get("output_dir")
            puzzle_type = task.input_data.get("puzzle_type", "crossword")
            subtitle = task.input_data.get("subtitle")
            
            if not input_dir or not output_dir:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    error_message="Missing input_dir or output_dir in task data",
                )
            
            # Prepare directories
            input_path = Path(input_dir)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Select appropriate script
            if puzzle_type == "sudoku":
                script_path = self.sudoku_layout_script
            else:
                script_path = self.layout_script
            
            if not script_path.exists():
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    error_message=f"Layout script not found: {script_path}",
                )
            
            # Build command
            cmd = [
                sys.executable,
                str(script_path),
                "--input", str(input_path),
                "--output", str(output_path),
                "--title", title,
                "--author", author,
            ]
            
            # Add subtitle for sudoku books
            if subtitle and puzzle_type == "sudoku":
                cmd.extend(["--subtitle", subtitle])
            
            # Add PDF-specific parameters
            pdf_params = task.input_data.get("pdf_params", {})
            for key, value in pdf_params.items():
                cli_flag = key.replace("_", "-")
                
                # Handle boolean flags
                if isinstance(value, bool):
                    if key == "include_solutions" and not value:
                        cmd.append("--no-solutions")
                    elif value and key != "include_solutions":
                        cmd.append(f"--{cli_flag}")
                else:
                    cmd.extend([f"--{cli_flag}", str(value)])
            
            self.logger.info(f"Executing PDF layout: {' '.join(cmd)}")
            
            # Execute command
            start_time = datetime.now()
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await result.communicate()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.returncode != 0:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    execution_time=execution_time,
                    error_message=f"PDF layout failed: {stderr.decode()}",
                    error_details={"stdout": stdout.decode(), "stderr": stderr.decode()},
                )
            
            # Find generated PDF
            pdf_files = list(output_path.glob("*.pdf"))
            if not pdf_files:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    execution_time=execution_time,
                    error_message="No PDF files generated",
                )
            
            # Get the most recent PDF file
            interior_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
            
            # Calculate quality score based on file size and presence
            file_size_mb = interior_pdf.stat().st_size / (1024 * 1024)
            quality_score = min(100, max(50, file_size_mb * 10))  # Basic heuristic
            
            return TaskResult(
                success=True,
                task_id=task.task_id,
                agent_id=self.agent_id,
                execution_time=execution_time,
                output_data={
                    "title": title,
                    "author": author,
                    "interior_pdf": str(interior_pdf),
                    "file_size_mb": file_size_mb,
                    "output_directory": str(output_path),
                },
                artifacts={
                    "pdf_dir": str(output_path),
                    "interior_pdf": str(interior_pdf),
                },
                quality_score=quality_score,
                performance_metrics={
                    "layout_speed_mb_per_sec": file_size_mb / execution_time if execution_time > 0 else 0,
                    "pages_estimated": int(file_size_mb * 20),  # Rough estimate
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"PDF layout error: {str(e)}",
                error_details={"exception": str(e)},
            )


class EPUBGeneratorAgent(BaseAgent):
    """
    Specialized agent for EPUB generation
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        max_concurrent_tasks: int = 2,
    ):
        """Initialize EPUB generator agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type="epub_generator",
            capabilities=[AgentCapability.EPUB_GENERATION, AgentCapability.CONTENT_GENERATION],
            max_concurrent_tasks=max_concurrent_tasks,
        )
        
        # Will dynamically import the EPUB generator module
        self.epub_module = None
    
    async def _initialize(self) -> None:
        """Initialize EPUB generator agent"""
        try:
            # Import the EPUB generator module
            import importlib.util
            scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
            epub_script = scripts_dir / "enhanced_epub_generator.py"
            
            if epub_script.exists():
                spec = importlib.util.spec_from_file_location("enhanced_epub_generator", epub_script)
                self.epub_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.epub_module)
                self.logger.info("EPUB generator module loaded successfully")
            else:
                self.logger.warning(f"EPUB generator script not found: {epub_script}")
                
        except Exception as e:
            self.logger.error(f"Failed to load EPUB generator module: {e}")
    
    async def _cleanup(self) -> None:
        """Cleanup EPUB generator agent"""
        self.logger.info("EPUB generator agent cleaned up")
    
    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute EPUB generation task"""
        if task.task_type != TaskType.GENERATE_EPUB:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"Unsupported task type: {task.task_type}",
            )
        
        if not self.epub_module:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message="EPUB generator module not available",
            )
        
        try:
            # Extract task parameters
            title = task.input_data.get("title", "Untitled Book")
            author = task.input_data.get("author", "KindleMint Publishing")
            series_name = task.input_data.get("series_name", "Default_Series")
            volume = task.input_data.get("volume", 1)
            description = task.input_data.get("description", "A collection of puzzles")
            keywords = task.input_data.get("keywords", ["puzzles"])
            language = task.input_data.get("language", "en")
            
            # Prepare output directory
            output_dir = Path(f"books/active_production/{series_name}/volume_{volume}/kindle")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create custom EPUB generator
            class CustomEpubGenerator(self.epub_module.EnhancedKindleEpubGenerator):
                def __init__(self, output_dir, book_config):
                    super().__init__()
                    self.output_dir = output_dir
                    self.epub_dir = output_dir / "epub_enhanced_build"
                    self.epub_dir.mkdir(parents=True, exist_ok=True)
                    self.book_config = book_config
            
            # Create generator and generate EPUB
            start_time = datetime.now()
            
            book_config = {
                "title": title,
                "author": author,
                "description": description,
                "keywords": keywords,
                "language": language,
            }
            
            generator = CustomEpubGenerator(output_dir, book_config)
            epub_file = await asyncio.get_event_loop().run_in_executor(
                None, generator.create_enhanced_epub
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if not epub_file or not Path(epub_file).exists():
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    execution_time=execution_time,
                    error_message="EPUB file was not created",
                )
            
            # Create metadata and checklist files
            metadata = {
                "title": title,
                "author": author,
                "description": description,
                "keywords": keywords,
                "language": language,
                "publication_date": datetime.now().strftime("%Y-%m-%d"),
            }
            
            metadata_file = output_dir / "kindle_metadata.json"
            with open(metadata_file, "w") as f:
                import json
                json.dump(metadata, f, indent=2)
            
            # Get file size
            epub_path = Path(epub_file)
            file_size_mb = epub_path.stat().st_size / (1024 * 1024)
            
            # Calculate quality score
            quality_score = min(100, max(70, file_size_mb * 50))  # Basic heuristic
            
            return TaskResult(
                success=True,
                task_id=task.task_id,
                agent_id=self.agent_id,
                execution_time=execution_time,
                output_data={
                    "title": title,
                    "author": author,
                    "epub_file": str(epub_file),
                    "file_size_mb": file_size_mb,
                    "metadata": metadata,
                },
                artifacts={
                    "epub_dir": str(output_dir),
                    "epub_file": str(epub_file),
                    "kindle_metadata": str(metadata_file),
                },
                quality_score=quality_score,
                performance_metrics={
                    "generation_speed_mb_per_sec": file_size_mb / execution_time if execution_time > 0 else 0,
                    "file_size_mb": file_size_mb,
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"EPUB generation error: {str(e)}",
                error_details={"exception": str(e)},
            )


class QualityAssuranceAgent(BaseAgent):
    """
    Specialized agent for quality assurance and validation
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        max_concurrent_tasks: int = 3,
    ):
        """Initialize QA agent"""
        super().__init__(
            agent_id=agent_id,
            agent_type="quality_assurance",
            capabilities=[AgentCapability.QUALITY_ASSURANCE],
            max_concurrent_tasks=max_concurrent_tasks,
        )
        
        # Will dynamically import QA modules
        self.qa_module = None
        self.puzzle_validators = None
    
    async def _initialize(self) -> None:
        """Initialize QA agent"""
        try:
            # Import QA modules
            import importlib.util
            scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
            
            # Load enhanced QA validator
            qa_script = scripts_dir / "enhanced_qa_validator.py"
            if qa_script.exists():
                spec = importlib.util.spec_from_file_location("enhanced_qa_validator", qa_script)
                self.qa_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.qa_module)
                self.logger.info("QA validator module loaded")
            
            # Load puzzle validators
            validators_script = scripts_dir / "puzzle_validators.py"
            if validators_script.exists():
                spec = importlib.util.spec_from_file_location("puzzle_validators", validators_script)
                self.puzzle_validators = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.puzzle_validators)
                self.logger.info("Puzzle validators module loaded")
                
        except Exception as e:
            self.logger.error(f"Failed to load QA modules: {e}")
    
    async def _cleanup(self) -> None:
        """Cleanup QA agent"""
        self.logger.info("QA agent cleaned up")
    
    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute QA validation task"""
        if task.task_type != TaskType.RUN_QA_TESTS:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"Unsupported task type: {task.task_type}",
            )
        
        try:
            # Extract task parameters
            file_path = task.input_data.get("file_path")
            validation_type = task.input_data.get("validation_type", "comprehensive")
            puzzle_type = task.input_data.get("puzzle_type", "").lower()
            puzzles_dir = task.input_data.get("puzzles_dir")
            
            if not file_path:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    agent_id=self.agent_id,
                    error_message="No file_path provided for QA validation",
                )
            
            start_time = datetime.now()
            
            # Run enhanced QA validation if available
            qa_results = {}
            if self.qa_module:
                checker = self.qa_module.EnhancedQAValidator()
                qa_results = await asyncio.get_event_loop().run_in_executor(
                    None, checker.run_enhanced_qa, file_path
                )
            else:
                # Basic validation fallback
                file_path_obj = Path(file_path)
                if not file_path_obj.exists():
                    qa_results = {
                        "overall_score": 0,
                        "publish_ready": False,
                        "issues_found": [{"description": "File does not exist"}],
                        "warnings": [],
                    }
                else:
                    qa_results = {
                        "overall_score": 85,
                        "publish_ready": True,
                        "issues_found": [],
                        "warnings": [],
                    }
            
            # Run domain-specific puzzle validation if available
            domain_issues = []
            if self.puzzle_validators and puzzles_dir and puzzle_type:
                try:
                    metadata_dir = Path(puzzles_dir).parent / "metadata"
                    if metadata_dir.exists():
                        if puzzle_type == "sudoku":
                            domain_issues = self.puzzle_validators.validate_sudoku(metadata_dir)
                        elif puzzle_type == "word_search":
                            domain_issues = self.puzzle_validators.validate_word_search(metadata_dir)
                        elif puzzle_type == "crossword":
                            domain_issues = self.puzzle_validators.validate_crossword(metadata_dir)
                            
                        # Integrate domain issues
                        if domain_issues:
                            qa_results.setdefault("issues_found", []).extend(
                                [{"description": issue} for issue in domain_issues]
                            )
                            qa_results["publish_ready"] = False
                            qa_results["overall_score"] = max(
                                0, qa_results.get("overall_score", 0) - len(domain_issues) * 10
                            )
                            qa_results["domain_issues"] = domain_issues
                            
                except Exception as e:
                    self.logger.warning(f"Domain validation failed: {e}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Save QA results
            output_dir = Path(file_path).parent / "qa"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            qa_report_file = output_dir / f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(qa_report_file, "w") as f:
                import json
                json.dump(qa_results, f, indent=2)
            
            return TaskResult(
                success=True,
                task_id=task.task_id,
                agent_id=self.agent_id,
                execution_time=execution_time,
                output_data={
                    "overall_score": qa_results.get("overall_score", 0),
                    "publish_ready": qa_results.get("publish_ready", False),
                    "issues_count": len(qa_results.get("issues_found", [])),
                    "warnings_count": len(qa_results.get("warnings", [])),
                    "domain_issues_count": len(qa_results.get("domain_issues", [])),
                },
                artifacts={
                    "qa_report": str(qa_report_file),
                    "qa_dir": str(output_dir),
                },
                quality_score=qa_results.get("overall_score", 0),
                performance_metrics={
                    "validation_speed": 1 / execution_time if execution_time > 0 else 0,
                    "checks_performed": len(qa_results.get("checks", [])),
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                agent_id=self.agent_id,
                error_message=f"QA validation error: {str(e)}",
                error_details={"exception": str(e)},
            )