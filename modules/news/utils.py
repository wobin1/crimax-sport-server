import re
from datetime import datetime

def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text"""
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

def calculate_read_time(content: str, words_per_minute: int = 200) -> int:
    """Calculate estimated read time in minutes based on word count"""
    words = len(content.split())
    minutes = max(1, round(words / words_per_minute))
    return minutes
