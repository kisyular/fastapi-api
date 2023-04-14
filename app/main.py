from fastapi import FastAPI

# import the routers
from .routers import post, user, auth, vote

# import models
from . import (
    models,  # The models help us to define the database models
)
from .database import engine

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

# CORS
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://nione.kisyula.com/",
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to my API"}


# Include the routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
