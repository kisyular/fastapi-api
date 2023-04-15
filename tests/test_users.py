from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app import schemas
from app.database import get_db, Base
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Welcome to my API"}


def test_create_user(client):
    response = client.post(
        "/users",
        json={"email": "musumbi@gmail.com", "password": "musumbi", "name": "Musumbi"},
    )
    schemas.UserResponse(
        **response.json()
    )  # convert the response to a UserResponse object

    assert response.status_code == 201


# def test_login_user(client, test_user):
#     print("Login User")
#     response = client.post(
#         "/login",
#         data={"username": test_user["email"], "password": test_user["password"]},
#     )
#     assert response.status_code == 200

#     token = response.json().get("access_token")
#     payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
#     id = payload.get("user_id")

#     assert id == test_user["id"]
#     assert response.json().get("token_type") == "bearer"

#     assert response.status_code == 200


# @pytest.mark.parametrize(
#     "email, password, status_code",
#     [
#         ("wrongemail@gmail.com", "password123", 403),
#         ("musumbi@gmail.com", "wrongpassword", 403),
#         ("wrongemail@gmail.com", "wrongpassword", 403),
#         (None, "password123", 422),
#         ("sanjeev@gmail.com", None, 422),
#     ],
# )
# def test_incorrect_login(client, test_user, email, password, status_code):
#     response = client.post("/login", data={"username": email, "password": password})

#     assert response.status_code == status_code
