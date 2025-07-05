"""
Email Module for KindleMint

Provides email automation and delivery functionality
"""

from .sendgrid_client import SendGridClient
from .email_automation import EmailAutomation

__all__ = ['SendGridClient', 'EmailAutomation']