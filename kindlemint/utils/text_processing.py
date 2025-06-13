"""Text processing utilities for the KindleMint engine."""
import re
import string
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str, remove_punctuation: bool = False) -> str:
    """Clean and normalize text.
    
    Args:
        text: Input text to clean
        remove_punctuation: Whether to remove all punctuation
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize whitespace and line breaks
    text = ' '.join(text.split())
    
    # Replace common Unicode characters with their ASCII equivalents
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('…', '...')
    
    # Remove control characters
    text = ''.join(char for char in text if char == '\n' or char == '\t' or not (0 <= ord(char) < 32))
    
    if remove_punctuation:
        # Remove all punctuation except apostrophes and hyphens in words
        text = re.sub(r'(?<!\w)[\'\"]+|[\'\"]+(?!\w)', '', text)
        text = re.sub(r'[^\w\s\'-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic heuristics.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Add spaces after sentence terminators if they don't exist
    text = re.sub(r'([.!?])([^\s\d])', r'\1 \2', text)
    
    # Split on sentence terminators
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out empty strings
    return [s.strip() for s in sentences if s.strip()]

def count_words(text: str) -> int:
    """Count the number of words in the text.
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    if not text:
        return 0
    return len(text.split())

def truncate_text(text: str, max_chars: int = 200, add_ellipsis: bool = True) -> str:
    """Truncate text to a maximum number of characters.
    
    Args:
        text: Input text
        max_chars: Maximum number of characters to keep
        add_ellipsis: Whether to add "..." at the end if text is truncated
        
    Returns:
        Truncated text
    """
    if not text or max_chars <= 0:
        return ""
    
    if len(text) <= max_chars:
        return text
    
    if add_ellipsis and max_chars > 3:
        return text[:max_chars - 3].rstrip() + '...'
    return text[:max_chars]

def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
    """Extract keywords from text.
    
    Args:
        text: Input text
        num_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Remove punctuation and convert to lowercase
    text = clean_text(text, remove_punctuation=True).lower()
    
    # Split into words and count frequencies
    words = text.split()
    word_counts = {}
    
    for word in words:
        if len(word) < 3:  # Skip very short words
            continue
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and get top N
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:num_keywords]]

def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate a URL-friendly slug from text.
    
    Args:
        text: Input text
        max_length: Maximum length of the generated slug
        
    Returns:
        URL-friendly slug
    """
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip().replace(' ', '-')
    
    # Remove all non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Trim to max length, making sure not to end with a hyphen
    if len(slug) > max_length:
        slug = slug[:max_length]
        if slug[-1] == '-':
            slug = slug[:-1]
    
    return slug
