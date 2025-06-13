"""Core book model and related functionality."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class BookMetadata:
    """Metadata for a book."""
    title: str
    subtitle: str = ""
    authors: List[str] = field(default_factory=list)
    description: str = ""
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    language: str = "en-US"
    publisher: str = ""
    publication_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    isbn: Optional[str] = None
    asin: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return asdict(self)

@dataclass
class BookContent:
    """Book content including chapters and other elements."""
    chapters: List[Dict[str, str]] = field(default_factory=list)  # List of {'title': str, 'content': str}
    front_matter: str = ""
    back_matter: str = ""
    
    def add_chapter(self, title: str, content: str) -> None:
        """Add a chapter to the book."""
        self.chapters.append({"title": title, "content": content})
    
    def get_word_count(self) -> int:
        """Get total word count of the book."""
        word_count = 0
        for chapter in self.chapters:
            word_count += len(chapter["content"].split())
        return word_count

class Book:
    """Main Book class representing a book in the publishing pipeline."""
    
    def __init__(self, title: str, author: str, content: Optional[BookContent] = None):
        """Initialize a new book.
        
        Args:
            title: Book title
            author: Main author name
            content: Optional BookContent instance
        """
        self.metadata = BookMetadata(title=title, authors=[author])
        self.content = content or BookContent()
        self.cover_path: Optional[Path] = None
        self.manuscript_path: Optional[Path] = None
        self._temp_files: List[Path] = []
    
    @property
    def title(self) -> str:
        """Get book title."""
        return self.metadata.title
    
    @property
    def author(self) -> str:
        """Get primary author name."""
        return self.metadata.authors[0] if self.metadata.authors else ""
    
    def add_author(self, name: str) -> None:
        """Add an author to the book."""
        if name not in self.metadata.authors:
            self.metadata.authors.append(name)
    
    def set_cover(self, image_path: Path) -> None:
        """Set the book cover image.
        
        Args:
            image_path: Path to cover image file
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Cover image not found: {image_path}")
        self.cover_path = image_path
    
    def save_metadata(self, file_path: Path) -> None:
        """Save book metadata to a JSON file.
        
        Args:
            file_path: Path to save metadata file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_metadata(self, file_path: Path) -> None:
        """Load book metadata from a JSON file.
        
        Args:
            file_path: Path to metadata file
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = BookMetadata(**data)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up temporary files."""
        self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up any temporary files."""
        for file_path in self._temp_files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {file_path}: {e}")
        self._temp_files = []
    
    def __del__(self):
        """Destructor - ensure cleanup."""
        self.cleanup()
