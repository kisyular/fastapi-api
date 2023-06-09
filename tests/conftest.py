from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import get_db, Base
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.oauth2 import create_access_token
from app import models

# Load environment variables from .env file
db_host = settings.db_host
db_port = settings.db_port
db_user = settings.db_user
db_password = settings.db_password
db_name = settings.db_name

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}_test"
)

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create SQLAlchemy session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    # run our code after we run our test
    Base.metadata.drop_all(bind=engine)
    # run our code before we run our test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    user_data = {
        "email": "musumbi@gmail.com",
        "password": "musumbi123",
        "name": "Musumbi",
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture()
def test_user2(client):
    user_data = {"email": "mfalme@gmail.com", "password": "mfalme123", "name": "Mfalme"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture()
def token(test_user):
    return create_access_token(data={"user_id": test_user["id"]})


@pytest.fixture()
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(session, test_user, test_user2):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "category": "first category",
            "owner_id": test_user["id"],
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "category": "2nd category",
            "owner_id": test_user["id"],
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "category": "3rd category",
            "owner_id": test_user2["id"],
        },
    ]

    def create_post_model(post_data):
        return models.Post(**post_data)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)

    session.commit()
    posts = session.query(models.Post).all()

    return posts
