"""
Stripe Metered Billing Integration

Pushes crawl usage records to Stripe for metered billing.
"""
import os
import time

import stripe

from kindlemint.billing.crawl_billing import crawl_billing_manager


class StripeMeteredBilling:
    """
    Handles pushing usage records to Stripe Metered Billing.
    """

    def __init__(self):
        api_key = os.getenv("STRIPE_SECRET_KEY")
        if not api_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")
        stripe.api_key = api_key
        self.subscription_item_id = os.getenv("STRIPE_SUBSCRIPTION_ITEM_ID")
        if not self.subscription_item_id:
            raise ValueError(
                "STRIPE_SUBSCRIPTION_ITEM_ID environment variable is required"
            )

    def push_usage(self) -> dict:
        """
        Push current crawl usage to Stripe as a UsageRecord.

        Returns:
            A dict with result status and Stripe record.
        """
        usage = crawl_billing_manager.usage_count
        if usage <= 0:
            return {"status": "no_usage"}

        record = stripe.UsageRecord.create(
            subscription_item=self.subscription_item_id,
            quantity=usage,
            timestamp=int(time.time()),
            action="increment",
        )
        # Reset local usage after successful push
        crawl_billing_manager.reset_usage()
        return {"status": "success", "record": record}

    def get_usage(self) -> int:
        """Get current unpushed usage count."""
        return crawl_billing_manager.usage_count
