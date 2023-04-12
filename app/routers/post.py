from .. import models, schemas, oauth2
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db

# Create a router
router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostResponse]
)
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    # sort posts by created date
    # posts.sort(key=lambda x: x.created_at, reverse=True)
    # return posts

    # sort posts by id
    posts.sort(key=lambda x: x.id, reverse=True)
    return posts


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    post: schemas.Post,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    print(current_user)
    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        category=post.category,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostResponse
)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    print(current_user.email)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    return post


@router.put(
    "/{id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.PostResponse,
)
def update_post(
    id: int,
    post: schemas.Post,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
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

    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    # deleting post
    deleted_post = (
        db.query(models.Post)
        .filter(models.Post.id == id)
        .delete(synchronize_session=False)
    )

    # Save post to deleted_posts table
    if post and deleted_post:
        deleted_post = models.DeletedPost(
            title=post.title,
            content=post.content,
            published=post.published,
            category=post.category,
            deleted_by=current_user.id,
        )
        db.add(deleted_post)

    db.commit()

    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Get Posts by Category
@router.get("/category/{category}")
def get_posts_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    posts = db.query(models.Post).filter(models.Post.category == category).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with category: {category} does not exist",
        )
    return posts


# Get Posts by Published
@router.get("/published/{published}")
def get_posts_by_published(
    published: bool,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    posts = db.query(models.Post).filter(models.Post.published == published).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with published: {published} does not exist",
        )
    return posts
