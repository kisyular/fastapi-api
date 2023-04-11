from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
import psycopg
import time
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# import models
from . import models
from .database import engine, get_db

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

# Load environment variables from .env file
load_dotenv()
import os

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

app = FastAPI()

# Database Connection
# Connect to the database using the psycopg library
while True:
    try:
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname="fastapi",
            row_factory=psycopg.rows.dict_row,
        )
        print("Connected to the database")
        cursor = conn.cursor()
        break
    except Exception as e:
        print("Error: ", e)
        print("Retrying in 5 seconds")
        time.sleep(5)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
    category: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        category=post.category,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    return {"data": post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if not post_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    post_query.update(
        {
            "title": post.title,
            "content": post.content,
            "published": post.published,
            "category": post.category,
        }
    )
    db.commit()

    return {"data": post_query.first()}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # deleting post
    deleted_post = (
        db.query(models.Post)
        .filter(models.Post.id == id)
        .delete(synchronize_session=False)
    )
    db.commit()

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Get Posts by Category
@app.get("/posts/category/{category}")
def get_posts_by_category(category: str, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.category == category).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with category: {category} does not exist",
        )
    return {"data": posts}


# Get Posts by Published
@app.get("/posts/published/{published}")
def get_posts_by_published(published: bool, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.published == published).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with published: {published} does not exist",
        )
    return {"data": posts}
