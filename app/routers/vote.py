from sqlalchemy import or_
from .. import models, schemas, oauth2
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import database, schemas, models, oauth2

# Create a router
router = APIRouter(prefix="/vote", tags=["Vote"])


# create a vote
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # Check if the post exists
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {vote.post_id} does not exist",
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id,
    )
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with id: {current_user.id} has already voted on post with id {vote.post_id}",
            )
        new_vote = models.Vote(
            post_id=vote.post_id,
            user_id=current_user.id,
        )
        db.add(new_vote)
        db.commit()
        return {"message": "Vote created successfully"}

    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {current_user.id} has not voted on post with id {vote.post_id}",
            )
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Vote deleted successfully"}
