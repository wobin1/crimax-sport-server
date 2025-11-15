from modules.shared.db import get_db_connection
from .models import NewsCreate, NewsUpdate, SectionCreate, SectionUpdate
from datetime import datetime
from typing import Optional, List

# ==================== SECTIONS MANAGEMENT ====================

async def get_sections(is_active: Optional[bool] = None):
    """Get all sections, optionally filtered by active status"""
    conn = await get_db_connection()
    try:
        if is_active is not None:
            sections = await conn.fetch(
                "SELECT * FROM sections WHERE is_active = $1 ORDER BY display_order, section_name",
                is_active
            )
        else:
            sections = await conn.fetch("SELECT * FROM sections ORDER BY display_order, section_name")
        return [dict(section) for section in sections]
    finally:
        await conn.close()

async def get_section_by_id(section_id: int):
    """Get a section by ID"""
    conn = await get_db_connection()
    try:
        section = await conn.fetchrow("SELECT * FROM sections WHERE section_id = $1", section_id)
        return dict(section) if section else None
    finally:
        await conn.close()

async def get_section_by_slug(slug: str):
    """Get a section by slug"""
    conn = await get_db_connection()
    try:
        section = await conn.fetchrow("SELECT * FROM sections WHERE slug = $1", slug)
        return dict(section) if section else None
    finally:
        await conn.close()

async def create_section(section: SectionCreate):
    """Create a new section"""
    conn = await get_db_connection()
    try:
        section_id = await conn.fetchval("""
            INSERT INTO sections (section_name, slug, description, display_order, is_active)
            VALUES ($1, $2, $3, $4, $5) RETURNING section_id
        """, section.section_name, section.slug, section.description, 
            section.display_order, section.is_active)
        return section_id
    finally:
        await conn.close()

async def update_section(section_id: int, section: SectionUpdate):
    """Update a section"""
    conn = await get_db_connection()
    try:
        # Build dynamic update query
        updates = []
        values = []
        param_count = 1
        
        if section.section_name is not None:
            updates.append(f"section_name = ${param_count}")
            values.append(section.section_name)
            param_count += 1
        
        if section.slug is not None:
            updates.append(f"slug = ${param_count}")
            values.append(section.slug)
            param_count += 1
        
        if section.description is not None:
            updates.append(f"description = ${param_count}")
            values.append(section.description)
            param_count += 1
        
        if section.display_order is not None:
            updates.append(f"display_order = ${param_count}")
            values.append(section.display_order)
            param_count += 1
        
        if section.is_active is not None:
            updates.append(f"is_active = ${param_count}")
            values.append(section.is_active)
            param_count += 1
        
        if not updates:
            return False
        
        updates.append(f"updated_at = ${param_count}")
        values.append(datetime.now())
        param_count += 1
        
        values.append(section_id)
        query = f"UPDATE sections SET {', '.join(updates)} WHERE section_id = ${param_count}"
        
        result = await conn.execute(query, *values)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_section(section_id: int):
    """Delete a section"""
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM sections WHERE section_id = $1", section_id)
        return result == "DELETE 1"
    finally:
        await conn.close()

# ==================== NEWS MANAGEMENT ====================

async def get_news_list(
    section_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    featured: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get news list with optional filters"""
    conn = await get_db_connection()
    try:
        query = """
            SELECT n.*, s.section_name
            FROM news n
            LEFT JOIN sections s ON n.section_id = s.section_id
            WHERE 1=1
        """
        params = []
        param_count = 1
        
        if section_id is not None:
            query += f" AND n.section_id = ${param_count}"
            params.append(section_id)
            param_count += 1
        
        if is_published is not None:
            query += f" AND n.is_published = ${param_count}"
            params.append(is_published)
            param_count += 1
        
        if featured is not None:
            query += f" AND n.featured = ${param_count}"
            params.append(featured)
            param_count += 1
        
        query += f" ORDER BY n.published_at DESC NULLS LAST, n.created_at DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        news = await conn.fetch(query, *params)
        return [dict(item) for item in news]
    finally:
        await conn.close()

async def get_news_by_id(news_id: int):
    """Get a news article by ID"""
    conn = await get_db_connection()
    try:
        news = await conn.fetchrow("""
            SELECT n.*, s.section_name
            FROM news n
            LEFT JOIN sections s ON n.section_id = s.section_id
            WHERE n.news_id = $1
        """, news_id)
        return dict(news) if news else None
    finally:
        await conn.close()

async def get_news_by_slug(slug: str):
    """Get a news article by slug"""
    conn = await get_db_connection()
    try:
        news = await conn.fetchrow("""
            SELECT n.*, s.section_name
            FROM news n
            LEFT JOIN sections s ON n.section_id = s.section_id
            WHERE n.slug = $1
        """, slug)
        return dict(news) if news else None
    finally:
        await conn.close()

async def create_news(news: NewsCreate, author_id: Optional[int] = None):
    """Create a new news article"""
    conn = await get_db_connection()
    try:
        published_at = datetime.now() if news.is_published else None
        
        news_id = await conn.fetchval("""
            INSERT INTO news (
                section_id, title, slug, excerpt, content, image,
                author_id, author_name, author_avatar, read_time, tags,
                featured, is_published, published_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING news_id
        """, news.section_id, news.title, news.slug, news.excerpt, news.content,
            news.image, author_id, news.author_name, news.author_avatar,
            news.read_time, news.tags, news.featured, news.is_published, published_at)
        return news_id
    finally:
        await conn.close()

async def update_news(news_id: int, news: NewsUpdate):
    """Update a news article"""
    conn = await get_db_connection()
    try:
        # Build dynamic update query
        updates = []
        values = []
        param_count = 1
        
        if news.section_id is not None:
            updates.append(f"section_id = ${param_count}")
            values.append(news.section_id)
            param_count += 1
        
        if news.title is not None:
            updates.append(f"title = ${param_count}")
            values.append(news.title)
            param_count += 1
        
        if news.slug is not None:
            updates.append(f"slug = ${param_count}")
            values.append(news.slug)
            param_count += 1
        
        if news.excerpt is not None:
            updates.append(f"excerpt = ${param_count}")
            values.append(news.excerpt)
            param_count += 1
        
        if news.content is not None:
            updates.append(f"content = ${param_count}")
            values.append(news.content)
            param_count += 1
        
        if news.image is not None:
            updates.append(f"image = ${param_count}")
            values.append(news.image)
            param_count += 1
        
        if news.author_name is not None:
            updates.append(f"author_name = ${param_count}")
            values.append(news.author_name)
            param_count += 1
        
        if news.author_avatar is not None:
            updates.append(f"author_avatar = ${param_count}")
            values.append(news.author_avatar)
            param_count += 1
        
        if news.read_time is not None:
            updates.append(f"read_time = ${param_count}")
            values.append(news.read_time)
            param_count += 1
        
        if news.tags is not None:
            updates.append(f"tags = ${param_count}")
            values.append(news.tags)
            param_count += 1
        
        if news.featured is not None:
            updates.append(f"featured = ${param_count}")
            values.append(news.featured)
            param_count += 1
        
        if news.is_published is not None:
            updates.append(f"is_published = ${param_count}")
            values.append(news.is_published)
            param_count += 1
            
            # Update published_at when publishing
            if news.is_published:
                updates.append(f"published_at = ${param_count}")
                values.append(datetime.now())
                param_count += 1
        
        if not updates:
            return False
        
        updates.append(f"updated_at = ${param_count}")
        values.append(datetime.now())
        param_count += 1
        
        values.append(news_id)
        query = f"UPDATE news SET {', '.join(updates)} WHERE news_id = ${param_count}"
        
        result = await conn.execute(query, *values)
        return result == "UPDATE 1"
    finally:
        await conn.close()

async def delete_news(news_id: int):
    """Delete a news article"""
    conn = await get_db_connection()
    try:
        result = await conn.execute("DELETE FROM news WHERE news_id = $1", news_id)
        return result == "DELETE 1"
    finally:
        await conn.close()

async def increment_news_views(news_id: int):
    """Increment view count for a news article"""
    conn = await get_db_connection()
    try:
        await conn.execute("UPDATE news SET views = views + 1 WHERE news_id = $1", news_id)
        return True
    finally:
        await conn.close()

async def get_news_count(section_id: Optional[int] = None, is_published: Optional[bool] = None):
    """Get total count of news articles"""
    conn = await get_db_connection()
    try:
        query = "SELECT COUNT(*) FROM news WHERE 1=1"
        params = []
        param_count = 1
        
        if section_id is not None:
            query += f" AND section_id = ${param_count}"
            params.append(section_id)
            param_count += 1
        
        if is_published is not None:
            query += f" AND is_published = ${param_count}"
            params.append(is_published)
            param_count += 1
        
        count = await conn.fetchval(query, *params)
        return count
    finally:
        await conn.close()
