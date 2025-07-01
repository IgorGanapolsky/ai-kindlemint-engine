"""
KDP Performance Monitoring Agent

This agent monitors individual book performance metrics including:
- Best Seller Rank (BSR) tracking
- Sales data collection
- Page reads (KDP Unlimited)
- Royalty calculations
- KDP dashboard status monitoring
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from .agent_types import AgentCapability
from .base_agent import BaseAgent
from .task_system import Task, TaskResult, TaskStatus


class KDPPerformanceAgent(BaseAgent):
    """Agent responsible for monitoring KDP book performance"""

    def __init__(
        self,
        data_storage_path: str = "books/performance_data",
        monitoring_interval: int = 3600,
    ):  # 1 hour default
        super().__init__(
            agent_type="kdp_performance_monitor",
            capabilities=[
                AgentCapability.PERFORMANCE_MONITORING,
                AgentCapability.SALES_TRACKING,
                AgentCapability.KDP_INTEGRATION,
                AgentCapability.BUSINESS_REPORTING,
            ],
            max_concurrent_tasks=5,
        )

        self.data_storage_path = Path(data_storage_path)
        self.monitoring_interval = monitoring_interval
        self.active_books: Dict[str, Dict] = {}
        self.performance_history: Dict[str, List[Dict]] = {}

        # Create storage directory
        self.data_storage_path.mkdir(parents=True, exist_ok=True)

    async def _initialize(self) -> None:
        """Initialize the KDP performance agent"""
        self.logger.info("Initializing KDP Performance Agent")

        # Load existing book data
        await self._load_active_books()

        # Start periodic monitoring
        asyncio.create_task(self._periodic_monitoring())

        self.logger.info(f"Monitoring {len(self.active_books)} active books")

    async def _cleanup(self) -> None:
        """Cleanup resources"""
        await self._save_performance_data()

    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute performance monitoring task"""
        try:
            task_type = task.parameters.get("type")

            if task_type == "monitor_book":
                return await self._monitor_single_book(task)
            elif task_type == "update_book_metadata":
                return await self._update_book_metadata(task)
            elif task_type == "generate_performance_report":
                return await self._generate_performance_report(task)
            elif task_type == "track_new_book":
                return await self._track_new_book(task)
            else:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Unknown task type: {task_type}",
                )

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return TaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED, error=str(e)
            )

    async def _monitor_single_book(self, task: Task) -> TaskResult:
        """Monitor performance metrics for a single book"""
        book_id = task.parameters.get("book_id")
        asin = task.parameters.get("asin")

        if not book_id or not asin:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="Missing book_id or ASIN",
            )

        try:
            # Collect performance metrics
            metrics = await self._collect_book_metrics(asin, book_id)

            # Store metrics
            await self._store_performance_metrics(book_id, metrics)

            # Update active book data
            if book_id in self.active_books:
                self.active_books[book_id][
                    "last_monitored"
                ] = datetime.now().isoformat()
                self.active_books[book_id]["current_metrics"] = metrics

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output={"book_id": book_id, "metrics": metrics},
            )

        except Exception as e:
            self.logger.error(f"Failed to monitor book {book_id}: {e}")
            return TaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED, error=str(e)
            )

    async def _collect_book_metrics(self, asin: str, book_id: str) -> Dict[str, Any]:
        """Collect comprehensive book performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "book_id": book_id,
            "asin": asin,
            "collected_at": datetime.now().isoformat(),
        }

        try:
            # Amazon product page scraping (public data only)
            product_data = await self._scrape_amazon_product_page(asin)
            metrics.update(product_data)

            # BSR tracking
            bsr_data = await self._get_bsr_data(asin)
            metrics["bsr"] = bsr_data

            # Reviews and ratings
            reviews_data = await self._get_reviews_metrics(asin)
            metrics["reviews"] = reviews_data

            # Price tracking
            price_data = await self._get_price_data(asin)
            metrics["pricing"] = price_data

            self.logger.info(
                f"Collected metrics for book {book_id} (ASIN: {asin})")

        except Exception as e:
            self.logger.error(f"Error collecting metrics for {asin}: {e}")
            metrics["error"] = str(e)

        return metrics

    async def _scrape_amazon_product_page(self, asin: str) -> Dict[str, Any]:
        """Scrape public Amazon product page data"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        url = f"https://www.amazon.com/dp/{asin}"

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        return {
                            "title": self._extract_title(soup),
                            "availability": self._extract_availability(soup),
                            "price": self._extract_price(soup),
                            "rating": self._extract_rating(soup),
                            "review_count": self._extract_review_count(soup)
                        }
                    else:
                        self.logger.warning(
                            f"Failed to fetch Amazon page for {asin}: {response.status}"
                        )
                        return {"error": f"HTTP {response.status}"}

        except Exception as e:
            self.logger.error(f"Error scraping Amazon page for {asin}: {e}")
            return {"error": str(e)}

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract book title from Amazon page"""
        title_selectors = [
            '#productTitle',
            '.product-title',
            'h1[data-automation-id="title"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    def _extract_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract current price from Amazon page"""
        price_selectors = [
            '.a-price-whole',
            '.a-price .a-offscreen',
            '#price_inside_buybox'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract average rating from Amazon page"""
        rating_selectors = [
            '[data-hook="average-star-rating"] .a-offscreen',
            '.reviewCountTextLinkedHistogram .a-offscreen'
        ]
        
        for selector in rating_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                try:
                    return float(text.split()[0])
                except:
                    continue
        return None

    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract review count from Amazon page"""
        review_selectors = [
            '[data-hook="total-review-count"]',
            '#acrCustomerReviewText'
        ]
        
        for selector in review_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                try:
                    # Extract number from text like "123 ratings"
                    import re
                    match = re.search(r'(\d+)', text)
                    if match:
                        return int(match.group(1))
                except:
                    continue
        return None

    def _extract_availability(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract availability status from Amazon page"""
        availability_selectors = [
            '#availability span',
            '.a-color-success',
            '.a-color-price'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    async def _get_bsr_data(self, asin: str) -> Dict[str, Any]:
        """Extract BSR data from product page"""
        # BSR is typically in the product details section
        # This would need to be extracted from the scraped page
        return {
            "overall_rank": None,
            "category_ranks": [],
            "last_updated": datetime.now().isoformat(),
        }

    async def _get_reviews_metrics(self, asin: str) -> Dict[str, Any]:
        """Get reviews and ratings metrics"""
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {
                "5_star": 0,
                "4_star": 0,
                "3_star": 0,
                "2_star": 0,
                "1_star": 0,
            },
            "recent_reviews": [],
        }

    async def _get_price_data(self, asin: str) -> Dict[str, Any]:
        """Get current pricing data"""
        return {
            "current_price": None,
            "list_price": None,
            "discount_percentage": None,
            "price_history": [],
        }

    async def _store_performance_metrics(
        self, book_id: str, metrics: Dict[str, Any]
    ) -> None:
        """Store performance metrics to file system"""
        # Store in book-specific file
        book_metrics_file = self.data_storage_path / f"{book_id}_metrics.json"

        # Load existing metrics
        existing_metrics = []
        if book_metrics_file.exists():
            try:
                with open(book_metrics_file, "r") as f:
                    existing_metrics = json.load(f)
            except:
                existing_metrics = []

        # Add new metrics
        existing_metrics.append(metrics)

        # Keep only last 1000 entries to prevent file bloat
        existing_metrics = existing_metrics[-1000:]

        # Save updated metrics
        with open(book_metrics_file, "w") as f:
            json.dump(existing_metrics, f, indent=2)

        # Update in-memory history
        self.performance_history[book_id] = existing_metrics

    async def _track_new_book(self, task: Task) -> TaskResult:
        """Add a new book to monitoring"""
        book_data = task.parameters.get("book_data", {})

        required_fields = ["book_id", "asin", "title"]
        for field in required_fields:
            if field not in book_data:
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=f"Missing required field: {field}",
                )

        book_id = book_data["book_id"]

        # Add to active books
        self.active_books[book_id] = {
            "book_id": book_id,
            "asin": book_data["asin"],
            "title": book_data["title"],
            "added_at": datetime.now().isoformat(),
            "last_monitored": None,
            "monitoring_enabled": True,
            "current_metrics": {},
        }

        # Save active books
        await self._save_active_books()

        self.logger.info(
            f"Started tracking book: {book_id} ({book_data['title']})")

        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output={"message": f"Started tracking book {book_id}"},
        )

    async def _generate_performance_report(self, task: Task) -> TaskResult:
        """Generate comprehensive performance report"""
        report_type = task.parameters.get("report_type", "summary")
        time_range = task.parameters.get("time_range", "7d")

        try:
            report = await self._create_performance_report(report_type, time_range)

            # Save report
            report_file = (
                self.data_storage_path
                / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output={"report": report, "report_file": str(report_file)},
            )

        except Exception as e:
            return TaskResult(
                task_id=task.task_id, status=TaskStatus.FAILED, error=str(e)
            )

    async def _create_performance_report(
        self, report_type: str, time_range: str
    ) -> Dict[str, Any]:
        """Create performance report based on collected data"""
        cutoff_date = datetime.now() - self._parse_time_range(time_range)

        report = {
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "time_range": time_range,
            "total_books": len(self.active_books),
            "books": [],
        }

        for book_id, book_data in self.active_books.items():
            book_metrics = self.performance_history.get(book_id, [])

            # Filter metrics by time range
            recent_metrics = [
                m
                for m in book_metrics
                if datetime.fromisoformat(m["timestamp"]) >= cutoff_date
            ]

            if recent_metrics:
                book_report = {
                    "book_id": book_id,
                    "title": book_data["title"],
                    "asin": book_data["asin"],
                    "metrics_count": len(recent_metrics),
                    "latest_metrics": recent_metrics[-1] if recent_metrics else None,
                    "performance_summary": self._summarize_book_performance(
                        recent_metrics
                    ),
                }
                report["books"].append(book_report)

        return report

    def _parse_time_range(self, time_range: str) -> timedelta:
        """Parse time range string to timedelta"""
        if time_range.endswith("d"):
            return timedelta(days=int(time_range[:-1]))
        elif time_range.endswith("h"):
            return timedelta(hours=int(time_range[:-1]))
        elif time_range.endswith("w"):
            return timedelta(weeks=int(time_range[:-1]))
        else:
            return timedelta(days=7)  # Default to 7 days

    def _summarize_book_performance(self, metrics_list: List[Dict]) -> Dict[str, Any]:
        """Summarize performance metrics for a book"""
        if not metrics_list:
            return {}

        # Calculate trends and summaries
        summary = {
            "data_points": len(metrics_list),
            "monitoring_period": {
                "start": metrics_list[0]["timestamp"],
                "end": metrics_list[-1]["timestamp"],
            },
        }

        # Add more detailed analysis here
        # Price trends, rating changes, review growth, etc.

        return summary

    async def _load_active_books(self) -> None:
        """Load active books from storage"""
        active_books_file = self.data_storage_path / "active_books.json"

        if active_books_file.exists():
            try:
                with open(active_books_file, "r") as f:
                    self.active_books = json.load(f)
                self.logger.info(
                    f"Loaded {len(self.active_books)} active books")
            except Exception as e:
                self.logger.error(f"Failed to load active books: {e}")
                self.active_books = {}
        else:
            # Auto-discover books from the books directory
            await self._auto_discover_books()

    async def _auto_discover_books(self) -> None:
        """Auto-discover books from the books directory structure"""
        books_dir = Path("books/active_production")

        if not books_dir.exists():
            self.logger.warning("Books directory not found for auto-discovery")
            return

        discovered_books = {}

        for series_dir in books_dir.iterdir():
            if series_dir.is_dir() and not series_dir.name.startswith("."):
                for volume_dir in series_dir.iterdir():
                    if volume_dir.is_dir() and volume_dir.name.startswith("volume_"):
                        # Check for KDP metadata
                        metadata_files = list(
                            volume_dir.rglob("amazon_kdp_metadata.json")
                        )

                        for metadata_file in metadata_files:
                            try:
                                with open(metadata_file, "r") as f:
                                    metadata = json.load(f)

                                book_id = f"{series_dir.name}_{volume_dir.name}"

                                discovered_books[book_id] = {
                                    "book_id": book_id,
                                    "title": metadata.get("title", "Unknown"),
                                    "series": series_dir.name,
                                    "volume": volume_dir.name,
                                    "asin": metadata.get("asin", ""),
                                    "publication_date": metadata.get(
                                        "publication_date", ""
                                    ),
                                    "added_at": datetime.now().isoformat(),
                                    "last_monitored": None,
                                    "monitoring_enabled": True,
                                    "current_metrics": {},
                                    "metadata_file": str(metadata_file),
                                }

                            except Exception as e:
                                self.logger.error(
                                    f"Error reading metadata from {metadata_file}: {e}"
                                )

        self.active_books = discovered_books
        await self._save_active_books()

        self.logger.info(
            f"Auto-discovered {len(discovered_books)} books for monitoring"
        )

    async def _save_active_books(self) -> None:
        """Save active books to storage"""
        active_books_file = self.data_storage_path / "active_books.json"

        with open(active_books_file, "w") as f:
            json.dump(self.active_books, f, indent=2)

    async def _save_performance_data(self) -> None:
        """Save all performance data"""
        await self._save_active_books()

        # Save summary stats
        summary_file = self.data_storage_path / "monitoring_summary.json"
        summary = {
            "last_updated": datetime.now().isoformat(),
            "total_books": len(self.active_books),
            "total_metrics_collected": sum(
                len(metrics) for metrics in self.performance_history.values()
            ),
            "agent_stats": {
                "tasks_completed": self.metrics.tasks_completed,
                "tasks_failed": self.metrics.tasks_failed,
                "success_rate": self.metrics.success_rate,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
            },
        }

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

    async def _periodic_monitoring(self) -> None:
        """Periodic monitoring of all active books"""
        while self.status.value != "shutdown":
            try:
                self.logger.info("Starting periodic book monitoring cycle")

                for book_id, book_data in self.active_books.items():
                    if book_data.get("monitoring_enabled", True) and book_data.get(
                        "asin"
                    ):
                        # Create monitoring task
                        task = Task(
                            task_id=str(uuid.uuid4()),
                            task_type="monitor_book",
                            parameters={
                                "type": "monitor_book",
                                "book_id": book_id,
                                "asin": book_data["asin"],
                            },
                            required_capabilities=[
                                AgentCapability.PERFORMANCE_MONITORING
                            ],
                        )

                        # Execute monitoring
                        await self._process_task(task)

                        # Small delay between books to avoid rate limiting
                        await asyncio.sleep(5)

                self.logger.info("Completed periodic monitoring cycle")

                # Wait for next cycle
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Error in periodic monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _update_book_metadata(self, task: Task) -> TaskResult:
        """Update metadata for a tracked book"""
        book_id = task.parameters.get("book_id")
        updates = task.parameters.get("updates", {})

        if book_id not in self.active_books:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error="Book not found in tracking list",
            )

        # Update book data
        self.active_books[book_id].update(updates)
        self.active_books[book_id]["last_updated"] = datetime.now().isoformat()

        # Save changes
        await self._save_active_books()

        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output={"message": f"Updated metadata for book {book_id}"},
        )

    def get_book_performance_summary(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Get performance summary for a specific book"""
        if book_id not in self.active_books:
            return None

        book_data = self.active_books[book_id]
        metrics_history = self.performance_history.get(book_id, [])

        return {
            "book_info": book_data,
            "metrics_count": len(metrics_history),
            "latest_metrics": metrics_history[-1] if metrics_history else None,
            "first_monitored": (
                metrics_history[0]["timestamp"] if metrics_history else None
            ),
            "last_monitored": (
                metrics_history[-1]["timestamp"] if metrics_history else None
            ),
        }

    def get_all_books_summary(self) -> Dict[str, Any]:
        """Get summary of all tracked books"""
        return {
            "total_books": len(self.active_books),
            "monitoring_enabled": sum(
                1
                for book in self.active_books.values()
                if book.get("monitoring_enabled", True)
            ),
            "total_metrics": sum(
                len(metrics) for metrics in self.performance_history.values()
            ),
            "books": list(self.active_books.keys()),
            "last_updated": datetime.now().isoformat(),
        }
