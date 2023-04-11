from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
import time
from dotenv import load_dotenv

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


my_posts = [
    {
        "id": 123,
        "title": "JavaScript",
        "content": "JavaScript is a popular programming language used to create interactive websites and web applications. It is a high-level, interpreted language that can be run on a variety of platforms.",
        "category": "Programming Language",
    },
    {
        "id": 2234,
        "title": "Python",
        "content": "Python is a popular high-level programming language used for general-purpose programming. It emphasizes code readability and supports multiple programming paradigms, including structured, object-oriented, and functional programming.",
        "category": "Programming Language",
    },
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts():
    cursor.execute("SELECT * FROM posts ORDER BY id")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(
        "INSERT INTO posts (title, content, published, category) VALUES (%s, %s, %s,  %s) RETURNING *",
        (post.title, post.content, post.published, post.category),
    )
    conn.commit()
    return {"data": post.dict()}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    return {"data": post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    # updating post
    cursor.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s, category = %s WHERE id = %s RETURNING *",
        (post.title, post.content, post.published, post.category, id),
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting post
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Get Posts by Category
@app.get("/posts/category/{category}")
def get_posts_by_category(category: str):
    cursor.execute("SELECT * FROM posts WHERE category = %s", (category,))
    posts = cursor.fetchall()
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with category: {category} does not exist",
        )
    return {"data": posts}


# Get Posts by Published
@app.get("/posts/published/{published}")
def get_posts_by_published(published: bool):
    cursor.execute("SELECT * FROM posts WHERE published = %s", (published,))
    posts = cursor.fetchall()
    return {"data": posts}
