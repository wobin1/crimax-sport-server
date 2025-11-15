from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from .manager import (
    get_sections, get_section_by_id, get_section_by_slug, create_section, update_section, delete_section,
    get_news_list, get_news_by_id, get_news_by_slug, create_news, update_news, delete_news,
    increment_news_views, get_news_count
)
from .models import (
    SectionCreate, SectionUpdate, SectionResponse,
    NewsCreate, NewsUpdate, NewsResponse, NewsListResponse
)
from modules.shared.response import success_response, error_response
from modules.auth.router import get_current_user

router = APIRouter()

# ==================== SECTIONS ENDPOINTS ====================

@router.get("/sections", response_model=None)
async def list_sections(is_active: Optional[bool] = None):
    """Get all sections, optionally filtered by active status"""
    sections = await get_sections(is_active)
    return success_response(sections)

@router.get("/sections/{section_id}", response_model=None)
async def get_section(section_id: int):
    """Get a section by ID"""
    section = await get_section_by_id(section_id)
    if not section:
        return error_response("Section not found", 404)
    return success_response(section)

@router.get("/sections/slug/{slug}", response_model=None)
async def get_section_slug(slug: str):
    """Get a section by slug"""
    section = await get_section_by_slug(slug)
    if not section:
        return error_response("Section not found", 404)
    return success_response(section)

@router.post("/sections", dependencies=[Depends(get_current_user)])
async def add_section(section: SectionCreate, current_user: dict = Depends(get_current_user)):
    """Create a new section (admin only)"""
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    
    # Check if slug already exists
    existing = await get_section_by_slug(section.slug)
    if existing:
        return error_response("Section with this slug already exists", 400)
    
    section_id = await create_section(section)
    return success_response({"section_id": section_id}, 201)

@router.put("/sections/{section_id}", dependencies=[Depends(get_current_user)])
async def edit_section(section_id: int, section: SectionUpdate, current_user: dict = Depends(get_current_user)):
    """Update a section (admin only)"""
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    
    # Check if section exists
    existing = await get_section_by_id(section_id)
    if not existing:
        return error_response("Section not found", 404)
    
    # Check if new slug conflicts with another section
    if section.slug:
        slug_check = await get_section_by_slug(section.slug)
        if slug_check and slug_check['section_id'] != section_id:
            return error_response("Section with this slug already exists", 400)
    
    updated = await update_section(section_id, section)
    if not updated:
        return error_response("Failed to update section", 400)
    return success_response({"message": "Section updated"})

@router.delete("/sections/{section_id}", dependencies=[Depends(get_current_user)])
async def remove_section(section_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a section (admin only)"""
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    
    deleted = await delete_section(section_id)
    if not deleted:
        return error_response("Section not found", 404)
    return success_response({"message": "Section deleted"})

# ==================== NEWS ENDPOINTS ====================

@router.get("/", response_model=None)
async def list_news(
    section_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    featured: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get news list with optional filters and pagination"""
    news = await get_news_list(section_id, is_published, featured, limit, offset)
    total = await get_news_count(section_id, is_published)
    return success_response({
        "news": news,
        "total": total,
        "limit": limit,
        "offset": offset
    })

@router.get("/{news_id}", response_model=None)
async def get_news(news_id: int, increment_view: bool = True):
    """Get a news article by ID"""
    news = await get_news_by_id(news_id)
    if not news:
        return error_response("News not found", 404)
    
    # Increment view count
    if increment_view:
        await increment_news_views(news_id)
        news['views'] = news.get('views', 0) + 1
    
    return success_response(news)

@router.get("/slug/{slug}", response_model=None)
async def get_news_slug(slug: str, increment_view: bool = True):
    """Get a news article by slug"""
    news = await get_news_by_slug(slug)
    if not news:
        return error_response("News not found", 404)
    
    # Increment view count
    if increment_view:
        await increment_news_views(news['news_id'])
        news['views'] = news.get('views', 0) + 1
    
    return success_response(news)

@router.post("/", dependencies=[Depends(get_current_user)])
async def add_news(news: NewsCreate, current_user: dict = Depends(get_current_user)):
    """Create a new news article (admin only)"""
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    
    # Check if slug already exists
    existing = await get_news_by_slug(news.slug)
    if existing:
        return error_response("News with this slug already exists", 400)
    
    # Verify section exists if provided
    if news.section_id:
        section = await get_section_by_id(news.section_id)
        if not section:
            return error_response("Section not found", 404)
    
    news_id = await create_news(news, current_user["user_id"])
    return success_response({"news_id": news_id}, 201)

@router.put("/{news_id}", dependencies=[Depends(get_current_user)])
async def edit_news(news_id: int, news: NewsUpdate, current_user: dict = Depends(get_current_user)):
    """Update a news article (admin only)"""
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    
    # Check if news exists
    existing = await get_news_by_id(news_id)
    if not existing:
        return error_response("News not found", 404)
    
    # Check if new slug conflicts with another news
    if news.slug:
        slug_check = await get_news_by_slug(news.slug)
        if slug_check and slug_check['news_id'] != news_id:
            return error_response("News with this slug already exists", 400)
    
    # Verify section exists if provided
    if news.section_id:
        section = await get_section_by_id(news.section_id)
        if not section:
            return error_response("Section not found", 404)
    
    updated = await update_news(news_id, news)
    if not updated:
        return error_response("Failed to update news", 400)
    return success_response({"message": "News updated"})

@router.delete("/{news_id}", dependencies=[Depends(get_current_user)])
async def remove_news(news_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a news article (admin only)"""
    if current_user["role"] != "admin":
        return error_response("Unauthorized", 403)
    
    deleted = await delete_news(news_id)
    if not deleted:
        return error_response("News not found", 404)
    return success_response({"message": "News deleted"})
