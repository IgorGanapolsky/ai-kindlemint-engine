"""
Payments module for KindleMint - Handle payment processing and checkout
"""

from .stripe_checkout import StripeCheckout

__all__ = ['StripeCheckout']