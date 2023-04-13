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
        owner_id=current_user.id,
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
    updated_post: schemas.Post,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"you are not authorized to update this post",
        )

    post_query.update(
        {
            "title": updated_post.title,
            "content": updated_post.content,
            "published": updated_post.published,
            "category": updated_post.category,
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
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    # deleting post
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"you are not authorized to delete this post",
        )

    deleted_post = post_query.delete(synchronize_session=False)

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

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Get Posts by Category
@router.get(
    "/category/{category}",
    response_model=List[schemas.PostResponse],
    status_code=status.HTTP_200_OK,
)
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
@router.get(
    "/published/{published}",
    response_model=List[schemas.PostResponse],
    status_code=status.HTTP_200_OK,
)
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


# Get deleted posts
@router.get(
    "/deleted/trash",
    response_model=List[schemas.DeletedPostResponse],
    status_code=status.HTTP_200_OK,
)
def get_deleted_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    deleted_posts = db.query(models.DeletedPost).all()

    if not deleted_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no deleted posts",
        )
    return deleted_posts
