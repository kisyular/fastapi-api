from .. import models, schemas, utils
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db

# Create a router
router = APIRouter(prefix="/users", tags=["Users"])


# Create a user in users path
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
    )
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email: {user.email} already exists",
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Get a user by id
@router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse
)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist",
        )
    return user


# Get all users
@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse]
)
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users
