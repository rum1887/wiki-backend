from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

bookmarks = Table(
    "bookmarks",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("article_id", ForeignKey("articles.id", ondelete="SET NULL"), primary_key=True),
    Column("created_at", DateTime, server_default=func.now())  
)

class UserArticleTag(Base):
    __tablename__ = "user_article_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String, nullable=False)  

    user = relationship("User", back_populates="tags")
    article = relationship("WikiArticle", back_populates="tags")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    saved_articles = relationship("WikiArticle", secondary=bookmarks, back_populates="bookmarked_by")
    tags = relationship("UserArticleTag", back_populates="user")  

class WikiArticle(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    summary = Column(String)

    bookmarked_by = relationship("User", secondary=bookmarks, back_populates="saved_articles")
    tags = relationship("UserArticleTag", back_populates="article")  
