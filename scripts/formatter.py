#!/usr/bin/env python3
"""
formatter.py: Defines a base Formatter interface for generating formatted manuscripts.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class Formatter(ABC):
    """
    Abstract base class for manuscript formatters.
    Concrete formatters should implement create_pdf().
    """

    @abstractmethod
    def create_pdf(self) -> Path:
        """
        Generate and save a PDF, returning its Path.
        """
        pass
