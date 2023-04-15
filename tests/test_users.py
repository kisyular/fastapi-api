from app import schemas
from jose import jwt
from app.config import settings
import pytest


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


def test_login_user(client, test_user):
    response = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200

    token = response.json().get("access_token")
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user["id"]
    assert response.json().get("token_type") == "bearer"

    assert response.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "password123", 403),
        ("musumbi@gmail.com", "wrongpassword", 403),
        ("wrongemail@gmail.com", "wrongpassword", 403),
        (None, "password123", 422),
        ("sanjeev@gmail.com", None, 422),
    ],
)
def test_incorrect_login(client, test_user, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})

    assert response.status_code == status_code
