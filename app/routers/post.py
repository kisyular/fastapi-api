from sqlalchemy import func, or_
from .. import models, schemas, oauth2
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from sqlalchemy.orm import joinedload

# Create a router
router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostWithVotes]
)
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    published: Optional[bool] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
):
    query = (
        db.query(models.Post, func.count(models.Vote.id).label("votes"))
        .outerjoin(models.Vote, models.Post.id == models.Vote.post_id)
        .group_by(models.Post.id)
    )
    if published is not None:
        query = query.filter(models.Post.published == published)
    if category is not None:
        query = query.filter(models.Post.category == category)
    if search:
        search_terms = search.split()
        search_pattern = "%" + "%".join(search_terms) + "%"
        query = query.filter(
            or_(
                models.Post.title.ilike(search_pattern),
                models.Post.content.ilike(search_pattern),
            )
        )
    # # get all posts sorted by id
    # posts = query.order_by(models.Post.id.desc()).offset(skip).limit(limit).all()

    # join the post and vote table
    results = (
        query.order_by(models.Post.id.desc())
        .options(joinedload(models.Post.votes))
        .offset(skip)
        .limit(limit)
        .all()
    )
    results = list(map(lambda x: x._mapping, results))
    return results


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    post: schemas.Post,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
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
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.PostWithVotes
)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post = (
        db.query(models.Post, func.count(models.Vote.id).label("votes"))
        .outerjoin(models.Vote, models.Post.id == models.Vote.post_id)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    post = post._mapping
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
            status_code=status.HTTP_403_FORBIDDEN,
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
            status_code=status.HTTP_403_FORBIDDEN,
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
            owner_id=current_user.id,
        )
        db.add(deleted_post)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    deleted_posts = (
        db.query(models.DeletedPost).order_by(models.DeletedPost.id.desc()).all()
    )

    if not deleted_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no deleted posts",
        )
    return deleted_posts
