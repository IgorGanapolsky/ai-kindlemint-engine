#!/usr/bin/env python3
"""
Enhanced Production Pipeline
Integrates parallel processing, templates, and quality validation
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import uuid

from parallel_book_processor import ParallelBookProcessor, BookJob
from template_manager import TemplateManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedProductionPipeline:
    """Complete production pipeline with all enhancements"""
    
    def __init__(self, max_workers: int = 4):
        self.processor = ParallelBookProcessor(max_workers=max_workers)
        self.template_manager = TemplateManager()
        self.production_stats = {
            "batches_processed": 0,
            "total_books": 0,
            "success_rate": 0.0,
            "templates_used": {}
        }
    
    async def produce_batch(self, batch_config: Dict) -> Dict:
        """Produce a batch of books based on configuration"""
        batch_id = str(uuid.uuid4())
        logger.info(f"Starting batch {batch_id}: {batch_config['name']}")
        
        # Validate batch configuration
        if not self._validate_batch_config(batch_config):
            raise ValueError("Invalid batch configuration")
        
        # Create jobs from batch configuration
        jobs = self._create_jobs_from_batch(batch_config, batch_id)
        
        # Add all jobs to processor
        self.processor.add_batch_jobs(jobs)
        
        # Start processing
        asyncio.create_task(self.processor.start_processing())
        
        # Monitor progress
        start_time = datetime.now()
        while self.processor.job_queue.qsize() > 0 or len(self.processor.active_jobs) > 0:
            status = self.processor.get_status()
            completion_rate = (
                status['metrics']['completed_jobs'] / 
                len(jobs) * 100 if jobs else 0
            )
            logger.info(f"Batch {batch_id}: {completion_rate:.1f}% complete")
            await asyncio.sleep(10)
        
        # Stop processor
        self.processor.stop_processing()
        
        # Calculate results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Update production stats
        self._update_production_stats(batch_config, jobs)
        
        results = {
            "batch_id": batch_id,
            "batch_name": batch_config['name'],
            "total_jobs": len(jobs),
            "completed": len(self.processor.completed_jobs),
            "failed": len(self.processor.failed_jobs),
            "duration_seconds": duration,
            "books_per_hour": len(self.processor.completed_jobs) / (duration / 3600) if duration > 0 else 0,
            "success_rate": len(self.processor.completed_jobs) / len(jobs) * 100 if jobs else 0
        }
        
        logger.info(f"Batch {batch_id} completed: {results}")
        return results
    
    def _validate_batch_config(self, config: Dict) -> bool:
        """Validate batch configuration"""
        required_fields = ['name', 'template', 'count', 'variations']
        return all(field in config for field in required_fields)
    
    def _create_jobs_from_batch(self, batch_config: Dict, batch_id: str) -> List[BookJob]:
        """Create book jobs from batch configuration"""
        jobs = []
        template = self.template_manager.get_template(batch_config['template'])
        
        if not template:
            raise ValueError(f"Template {batch_config['template']} not found")
        
        base_title = batch_config.get('base_title', template.name)
        variations = batch_config['variations']
        
        for i in range(batch_config['count']):
            # Cycle through variations
            variation = variations[i % len(variations)]
            
            # Apply template with variation
            params = self.template_manager.apply_template(
                batch_config['template'],
                variation
            )
            
            job = BookJob(
                job_id=f"{batch_id}_{i:04d}",
                title=f"{base_title} - {variation.get('subtitle', f'Volume {i+1}')}",
                category=template.category,
                priority=batch_config.get('priority', 5),
                template=batch_config['template'],
                params=params
            )
            
            jobs.append(job)
        
        return jobs
    
    def _update_production_stats(self, batch_config: Dict, jobs: List[BookJob]):
        """Update production statistics"""
        self.production_stats['batches_processed'] += 1
        self.production_stats['total_books'] += len(jobs)
        
        # Track template usage
        template = batch_config['template']
        if template not in self.production_stats['templates_used']:
            self.production_stats['templates_used'][template] = 0
        self.production_stats['templates_used'][template] += len(jobs)
        
        # Calculate overall success rate
        total_completed = sum(
            stats['completed'] 
            for stats in self.production_stats.get('batch_results', [])
        )
        if self.production_stats['total_books'] > 0:
            self.production_stats['success_rate'] = (
                total_completed / self.production_stats['total_books'] * 100
            )
    
    async def produce_daily_catalog(self) -> Dict:
        """Produce daily catalog of books across multiple categories"""
        daily_batches = [
            {
                "name": "Morning Puzzles",
                "template": "premium_puzzle_pack",
                "count": 10,
                "priority": 8,
                "base_title": "Morning Brain Training",
                "variations": [
                    {"subtitle": "Easy Start", "difficulty_levels": ["easy"]},
                    {"subtitle": "Medium Challenge", "difficulty_levels": ["medium"]},
                    {"subtitle": "Expert Edition", "difficulty_levels": ["hard", "expert"]}
                ]
            },
            {
                "name": "Senior Series",
                "template": "beginner_series",
                "count": 5,
                "priority": 9,
                "base_title": "Large Print Puzzles",
                "variations": [
                    {"subtitle": "Gentle Mind", "puzzle_types": ["sudoku_4x4"]},
                    {"subtitle": "Word Fun", "puzzle_types": ["simple_word_search"]}
                ]
            },
            {
                "name": "Themed Collection",
                "template": "premium_puzzle_pack",
                "count": 5,
                "priority": 7,
                "base_title": "Themed Puzzles",
                "variations": [
                    {"subtitle": "Nature Theme", "theme": "nature"},
                    {"subtitle": "Travel Theme", "theme": "travel"},
                    {"subtitle": "History Theme", "theme": "history"}
                ]
            }
        ]
        
        all_results = []
        
        for batch in daily_batches:
            try:
                result = await self.produce_batch(batch)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to produce batch {batch['name']}: {e}")
        
        # Generate daily report
        daily_report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "batches": all_results,
            "total_books_produced": sum(r['completed'] for r in all_results),
            "average_books_per_hour": sum(r['books_per_hour'] for r in all_results) / len(all_results) if all_results else 0,
            "production_stats": self.production_stats
        }
        
        # Save report
        report_path = Path("reports/daily_production") / f"report_{daily_report['date']}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(daily_report, f, indent=2)
        
        logger.info(f"Daily production complete: {daily_report['total_books_produced']} books produced")
        return daily_report
    
    def get_production_metrics(self) -> Dict:
        """Get overall production metrics"""
        return {
            "total_batches": self.production_stats['batches_processed'],
            "total_books": self.production_stats['total_books'],
            "success_rate": self.production_stats['success_rate'],
            "most_used_template": max(
                self.production_stats['templates_used'].items(),
                key=lambda x: x[1]
            )[0] if self.production_stats['templates_used'] else None,
            "templates_breakdown": self.production_stats['templates_used']
        }


# Example usage
async def main():
    """Run enhanced production pipeline"""
    pipeline = EnhancedProductionPipeline(max_workers=6)
    
    # Run daily catalog production
    report = await pipeline.produce_daily_catalog()
    
    print("\nDaily Production Report:")
    print(f"Date: {report['date']}")
    print(f"Total Books: {report['total_books_produced']}")
    print(f"Average Rate: {report['average_books_per_hour']:.1f} books/hour")
    
    # Get overall metrics
    metrics = pipeline.get_production_metrics()
    print("\nProduction Metrics:")
    print(f"Total Batches: {metrics['total_batches']}")
    print(f"Success Rate: {metrics['success_rate']:.1f}%")
    print(f"Most Used Template: {metrics['most_used_template']}")


if __name__ == "__main__":
    asyncio.run(main())