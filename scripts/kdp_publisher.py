#!/usr/bin/env python3
"""
KDP Publisher: Unified interface for KDP automation.
Wraps the existing Sentry-monitored KDP logic in a consolidated class.
"""

from sentry_kdp_automation import SentryKDPPublisher


class KdpPublisher(SentryKDPPublisher):
    """
    Consolidated publisher class for Kindle Direct Publishing.
    Inherits monitoring and error-handling from SentryKDPPublisher.
    """

    def __init__(self):
        super().__init__()

    def upload_book(self, book_metadata: dict) -> dict:
        """
        Execute the full KDP upload process for a single book.

        Args:
            book_metadata: Dictionary with book fields (title, format, price, etc.)

        Returns:
            A dict summarizing success, ASIN, and metadata of the publishing run.
        """
        return self.simulate_kdp_upload_process(book_metadata)


"""
Example usage in a script:
    from kdp_publisher import KdpPublisher
    publisher = KdpPublisher()
    result = publisher.upload_book(book_data)
"""
