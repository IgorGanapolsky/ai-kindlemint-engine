import os
import threading

class CrawlBillingManager:
    """
    Manager for crawl usage billing.
    Tracks number of crawl requests and calculates charges based on configured price.
    """
    def __init__(self):
        price = os.getenv("PRICE_PER_CRAWL", "0.00001")
        try:
            self.price_per_crawl = float(price)
        except ValueError:
            self.price_per_crawl = 0.00001
        self._lock = threading.Lock()
        self._usage_count = 0

    def record_crawl(self, count: int = 1) -> None:
        """
        Record crawl usage.

        Args:
            count: Number of crawl requests to add.
        """
        with self._lock:
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

# Global instance for recording crawl usage across agents.
crawl_billing_manager = CrawlBillingManager()
