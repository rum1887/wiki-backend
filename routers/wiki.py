from fastapi import APIRouter, Depends, Query, Body, HTTPException
from auth.auth_handler import get_current_active_user
from wiki_article.article_fetch import search_wikipedia
from schemas import UserResponse, WikiArticleSchema
from models import User, WikiArticle, UserArticleTag, bookmarks
from sqlalchemy.orm import Session, joinedload
from database import get_db
from typing import List
from urllib.parse import unquote
from llm import generate_tags

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search_wiki")
def search(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) 
):
    print(f"User {current_user.username if current_user else 'Anonymous'} searching for: {query}") 
    results = search_wikipedia(query) 
    # print(f"Backend Search Results: {results}")
    return results

@router.post("/save_article", response_model=dict)
def save_article(
    article: WikiArticleSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  
):
    print(f"Saving article for user: {current_user.username}")

    existing_article = db.query(WikiArticle).filter(WikiArticle.url == article.url).first()
    if existing_article:
        article.id = existing_article.id  
    else:
        new_article = WikiArticle(**article.model_dump(exclude={"id"}))  
        db.add(new_article)
        db.flush() 
        article.id = new_article.id 

    existing_bookmark = db.query(bookmarks).filter(
        (bookmarks.c.article_id == article.id) &
        (bookmarks.c.user_id == current_user.id)
    ).first()

    if not existing_bookmark:
        db.execute(bookmarks.insert().values(user_id=current_user.id, article_id=article.id))

    tag_response = generate_tags(article.summary, article.url)
    tag_names = [tag.strip() for tag in tag_response.split(",")]

    existing_tags = db.query(UserArticleTag).filter(
        UserArticleTag.article_id == article.id,
        UserArticleTag.user_id == current_user.id,
        UserArticleTag.tag_name.in_(tag_names)  
    ).all()
    existing_tag_names = {tag.tag_name for tag in existing_tags}  

    new_tags = [
        UserArticleTag(user_id=current_user.id, article_id=article.id, tag_name=tag_name)
        for tag_name in tag_names if tag_name not in existing_tag_names
    ]
    db.add_all(new_tags)  

    db.commit()
    
    return {
        "message": "Article saved successfully!",
        "article_id": article.id,
        "tags": tag_names
    }

@router.delete("/unsave_article")
def unsave_article(
    article_url: str = Query(...),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    print(f"Received request to remove bookmark for: {article_url} by user {current_user.username}")

    existing_article = db.query(WikiArticle).filter(WikiArticle.url == article_url).first()
    if not existing_article:
        return {"message": "Article not found!"}

    existing_bookmark = db.execute(
        bookmarks.select().where(
            (bookmarks.c.article_id == existing_article.id) &
            (bookmarks.c.user_id == current_user.id)
        )
    ).fetchone()

    if not existing_bookmark:
        return {"message": "You have not bookmarked this article!"}

    db.execute(bookmarks.delete().where(
        (bookmarks.c.article_id == existing_article.id) &
        (bookmarks.c.user_id == current_user.id)
    ))

    db.commit()
    
    return {"message": "Bookmark removed!"}

@router.get("/get_saved_articles", response_model=List[WikiArticleSchema])
def get_saved_articles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    articles = db.query(WikiArticle).join(bookmarks).filter(
    bookmarks.c.user_id == current_user.id).options(joinedload(WikiArticle.tags)).all()

    for article in articles:
        print(f"Title: {article.title}, Tags: {[tag.tag_name for tag in article.tags]}")

    return articles


@router.put("/update_tags")
def update_tags(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  
):
    article_url = data.get("article_url")
    tags = data.get("tags", [])
    
    print(f"Updating tags for: {article_url} by user {current_user.username}")
    print(f"Received tags: {tags}")

    article = db.query(WikiArticle).filter(WikiArticle.url == article_url).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    try:
        existing_tags = db.query(UserArticleTag).filter(
            UserArticleTag.user_id == current_user.id,
            UserArticleTag.article_id == article.id
        ).all()

        existing_tag_names = {tag.tag_name for tag in existing_tags}

        tags_to_delete = [tag for tag in existing_tags if tag.tag_name not in tags]
        for tag in tags_to_delete:
            db.delete(tag)

        new_tags = [
            UserArticleTag(user_id=current_user.id, article_id=article.id, tag_name=tag_name)
            for tag_name in tags if tag_name not in existing_tag_names
        ]
        db.add_all(new_tags)

        db.commit()
        return {"message": "Tags updated successfully", "tags": tags}

    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"Error updating tags: {str(e)}")
