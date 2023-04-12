from fastapi import FastAPI

# import the routers
from .routers import post, user, auth

# import models
from . import (
    models,  # The models help us to define the database models
)
from .database import engine, get_db

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


# Include the routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
