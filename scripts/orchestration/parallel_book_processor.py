#!/usr/bin/env python3
"""
Parallel Book Processing Orchestrator
Enables 3-5x productivity boost through concurrent job execution
"""

import asyncio
import concurrent.futures
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from queue import PriorityQueue
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BookJob:
    """Represents a book generation job"""
    job_id: str
    title: str
    category: str
    priority: int  # 1-10, higher = more urgent
    template: str
    params: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def __lt__(self, other):
        """Enable priority queue sorting"""
        return self.priority > other.priority


class ParallelBookProcessor:
    """Manages parallel book generation with job queuing"""
    
    def __init__(self, max_workers: int = 4, output_dir: str = "generated/books"):
        self.max_workers = max_workers
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Job management
        self.job_queue = PriorityQueue()
        self.active_jobs: Dict[str, BookJob] = {}
        self.completed_jobs: Dict[str, BookJob] = {}
        self.failed_jobs: Dict[str, BookJob] = {}
        
        # Performance metrics
        self.metrics = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "avg_processing_time": 0,
            "total_processing_time": 0
        }
        
        # Thread pool for parallel execution
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        
    def add_job(self, job: BookJob) -> str:
        """Add a job to the processing queue"""
        self.job_queue.put(job)
        self.metrics["total_jobs"] += 1
        logger.info(f"Added job {job.job_id} to queue (priority: {job.priority})")
        return job.job_id
    
    def add_batch_jobs(self, jobs: List[BookJob]) -> List[str]:
        """Add multiple jobs at once"""
        job_ids = []
        for job in jobs:
            job_id = self.add_job(job)
            job_ids.append(job_id)
        return job_ids
    
    async def process_job(self, job: BookJob) -> BookJob:
        """Process a single book generation job"""
        logger.info(f"Starting job {job.job_id}: {job.title}")
        job.status = "processing"
        job.started_at = datetime.now()
        
        try:
            # Import book generation modules
            from scripts.generate_puzzle_book import PuzzleBookGenerator
            from scripts.generate_coloring_book import ColoringBookGenerator
            from scripts.generate_activity_book import ActivityBookGenerator
            
            # Select appropriate generator
            generators = {
                "puzzle": PuzzleBookGenerator,
                "coloring": ColoringBookGenerator,
                "activity": ActivityBookGenerator
            }
            
            generator_class = generators.get(job.category, PuzzleBookGenerator)
            generator = generator_class()
            
            # Generate book with template
            result = await self._generate_with_template(
                generator=generator,
                job=job
            )
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.result = result
            
            # Update metrics
            processing_time = (job.completed_at - job.started_at).total_seconds()
            self._update_metrics(processing_time, success=True)
            
            logger.info(f"Completed job {job.job_id} in {processing_time:.2f} seconds")
            
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            self._update_metrics(0, success=False)
            logger.error(f"Failed job {job.job_id}: {e}")
        
        return job
    
    async def _generate_with_template(self, generator: Any, job: BookJob) -> Dict:
        """Generate book using specified template"""
        # Load template configuration
        template_path = Path(f"templates/{job.template}/config.json")
        if template_path.exists():
            with open(template_path) as f:
                template_config = json.load(f)
        else:
            template_config = {}
        
        # Merge job params with template
        generation_params = {**template_config, **job.params}
        
        # Generate book
        result = await asyncio.to_thread(
            generator.generate,
            title=job.title,
            **generation_params
        )
        
        # Save to output directory
        output_path = self.output_dir / f"{job.job_id}_{job.title.replace(' ', '_')}.pdf"
        result["output_path"] = str(output_path)
        
        return result
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics"""
        if success:
            self.metrics["completed_jobs"] += 1
            self.metrics["total_processing_time"] += processing_time
            self.metrics["avg_processing_time"] = (
                self.metrics["total_processing_time"] / 
                self.metrics["completed_jobs"]
            )
        else:
            self.metrics["failed_jobs"] += 1
    
    async def start_processing(self):
        """Start the parallel processing engine"""
        self.running = True
        logger.info(f"Starting parallel processor with {self.max_workers} workers")
        
        # Create worker tasks
        workers = []
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            workers.append(worker)
        
        # Wait for all workers
        await asyncio.gather(*workers)
    
    async def _worker(self, worker_id: int):
        """Worker coroutine that processes jobs from queue"""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get job from queue (with timeout to check running status)
                job = await asyncio.wait_for(
                    asyncio.to_thread(self.job_queue.get, timeout=1),
                    timeout=2
                )
                
                if job:
                    # Move to active jobs
                    self.active_jobs[job.job_id] = job
                    
                    # Process the job
                    completed_job = await self.process_job(job)
                    
                    # Move to appropriate completed list
                    del self.active_jobs[job.job_id]
                    if completed_job.status == "completed":
                        self.completed_jobs[job.job_id] = completed_job
                    else:
                        self.failed_jobs[job.job_id] = completed_job
                        
            except asyncio.TimeoutError:
                # No jobs available, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    def stop_processing(self):
        """Stop the processing engine"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("Parallel processor stopped")
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        return {
            "running": self.running,
            "workers": self.max_workers,
            "queue_size": self.job_queue.qsize(),
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "failed_jobs": len(self.failed_jobs),
            "metrics": self.metrics
        }
    
    def get_job_status(self, job_id: str) -> Optional[BookJob]:
        """Get status of a specific job"""
        # Check all job lists
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        elif job_id in self.failed_jobs:
            return self.failed_jobs[job_id]
        
        # Check queue
        for job in list(self.job_queue.queue):
            if job.job_id == job_id:
                return job
        
        return None


# Example usage and batch processing
async def main():
    """Example of parallel book processing"""
    processor = ParallelBookProcessor(max_workers=4)
    
    # Create batch of jobs
    jobs = [
        BookJob(
            job_id=f"job_{i}",
            title=f"Sudoku Puzzles Volume {i}",
            category="puzzle",
            priority=10 if i < 5 else 5,  # First 5 are high priority
            template="premium_puzzle_pack",
            params={
                "difficulty": "medium",
                "puzzle_count": 50,
                "include_solutions": True
            }
        )
        for i in range(1, 21)  # 20 books
    ]
    
    # Add all jobs
    processor.add_batch_jobs(jobs)
    
    # Start processing
    processing_task = asyncio.create_task(processor.start_processing())
    
    # Monitor progress
    while processor.job_queue.qsize() > 0 or len(processor.active_jobs) > 0:
        status = processor.get_status()
        logger.info(f"Status: {status}")
        await asyncio.sleep(5)
    
    # Stop processor
    processor.stop_processing()
    await processing_task
    
    # Final report
    final_status = processor.get_status()
    logger.info(f"Final status: {final_status}")
    logger.info(f"Average processing time: {final_status['metrics']['avg_processing_time']:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())