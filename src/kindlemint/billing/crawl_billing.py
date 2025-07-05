import os
import threading
import logging

class CrawlBillingManager:
    """
    Manager for crawl usage billing.
    Tracks number of crawl requests and calculates charges based on configured price.
    """
    class CrawlBudgetExceeded(Exception):
        """Raised when crawl usage exceeds configured budget"""
        pass

    def __init__(self):
        price = os.getenv("PRICE_PER_CRAWL", "0.00001")
        try:
            self.price_per_crawl = float(price)
        except ValueError:
            logging.getLogger(__name__).warning(
                f"Invalid PRICE_PER_CRAWL '{price}', defaulting to 0.00001"
            )
            self.price_per_crawl = 0.00001
        # Optional budget threshold (in same units as cost)
        budget = os.getenv("MAX_CRAWL_BUDGET")
        try:
            self.budget = float(budget) if budget is not None else None
        except ValueError:
            logging.getLogger(__name__).warning(
                f"Invalid MAX_CRAWL_BUDGET '{budget}', ignoring budget"
            )
            self.budget = None
        self._lock = threading.Lock()
        self._usage_count = 0
        self._budget_exceeded = False

    def record_crawl(self, count: int = 1) -> None:
        """
        Record crawl usage.

        Args:
            count: Number of crawl requests to add.
        """
        with self._lock:
            projected_cost = (self._usage_count + count) * self.price_per_crawl
            if self.budget is not None and projected_cost > self.budget:
                self._budget_exceeded = True
                raise CrawlBillingManager.CrawlBudgetExceeded(
                    f"Crawl budget exceeded: attempted cost {projected_cost} > budget {self.budget}"
                )
            self._usage_count += count

    @property
    def usage_count(self) -> int:
        """Return total recorded crawl requests."""
        with self._lock:
            return self._usage_count

    def calculate_charge(self) -> float:
        """
        Calculate total charge based on usage.

        Returns:
            Total cost as float.
        """
        return self.usage_count * self.price_per_crawl

    def reset_usage(self) -> None:
        """Reset the recorded usage count to zero."""
        with self._lock:
            self._usage_count = 0
        # reset budget flag
        self._budget_exceeded = False

    @property
    def budget_exceeded(self) -> bool:
        """Indicates if the configured budget has been exceeded."""
        return self._budget_exceeded

# Global instance for recording crawl usage across agents.
crawl_billing_manager = CrawlBillingManager()
