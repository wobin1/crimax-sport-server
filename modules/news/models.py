from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Section Models
class SectionCreate(BaseModel):
    section_name: str
    slug: str
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class SectionUpdate(BaseModel):
    section_name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class SectionResponse(BaseModel):
    section_id: int
    section_name: str
    slug: str
    description: Optional[str]
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

# News Models
class NewsCreate(BaseModel):
    section_id: Optional[int] = None
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    image: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    read_time: int = 5
    tags: List[str] = []
    featured: bool = False
    is_published: bool = False

class NewsUpdate(BaseModel):
    section_id: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    read_time: Optional[int] = None
    tags: Optional[List[str]] = None
    featured: Optional[bool] = None
    is_published: Optional[bool] = None

class NewsResponse(BaseModel):
    news_id: int
    section_id: Optional[int]
    title: str
    slug: str
    excerpt: Optional[str]
    content: str
    image: Optional[str]
    author_id: Optional[int]
    author_name: Optional[str]
    author_avatar: Optional[str]
    read_time: int
    tags: List[str]
    featured: bool
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    views: int
    section_name: Optional[str] = None

class NewsListResponse(BaseModel):
    news_id: int
    section_id: Optional[int]
    title: str
    slug: str
    excerpt: Optional[str]
    image: Optional[str]
    author_name: Optional[str]
    read_time: int
    tags: List[str]
    featured: bool
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    views: int
    section_name: Optional[str] = None
