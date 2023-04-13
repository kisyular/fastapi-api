from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP


# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    posts = relationship("Post", back_populates="owner", cascade="all, delete")


# Post model
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default="false")
    category = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User", back_populates="posts")


# Deleted Post model
class DeletedPost(Base):
    __tablename__ = "deleted_posts"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, nullable=False, server_default="false")
    category = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    deleted_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    owner = relationship("User", back_populates="deleted_posts")

    # User model
    User.deleted_posts = relationship(
        "DeletedPost", back_populates="owner", cascade="all, delete"
    )
