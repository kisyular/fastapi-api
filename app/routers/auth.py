from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, oauth2, utils
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    tags=["Authentication"],
)


# Login route
@router.post("/login")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Remember that we are using OAuth2PasswordRequestForm which returns a username and password
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_NOT_FOUND,
            detail="Incorrect email or password",
        )
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_NOT_FOUND,
            detail="Incorrect password or email",
        )
    # Generate a JWT token
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
