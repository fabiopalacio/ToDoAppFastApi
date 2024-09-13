from fastapi import HTTPException
import pytest
from jose import jwt
from datetime import timedelta
from fastapi.testclient import TestClient

from main import app
from routers.utils import ALGORITHM, SECRET_KEY, authenticate_user, create_access_token, get_current_user
from routers.utils import get_db
from tests.utils import TestingSessionLocal, override_get_current_user, override_get_db
from tests.utils import test_user as test_user_fixtures

test_user = test_user_fixtures

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client = TestClient(app)


def test_authenticate_user_with_valid_user(test_user):
    db = TestingSessionLocal()
    response = authenticate_user(test_user.username, '1234', db)

    assert response.username == test_user.username


def test_authenticate_user_with_invalid_password(test_user):
    db = TestingSessionLocal()
    response = authenticate_user(test_user.username, 'wrongPassword', db)

    assert response is False


def test_authenticate_user_with_invalid_user(test_user):
    db = TestingSessionLocal()
    response = authenticate_user('invalid_user', '1234', db)

    assert response is False


def test_create_access_token():
    username = 'my_username'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(
        username=username,
        user_id=user_id,
        role=role,
        expires_delta=expires_delta
    )

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[
                               ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testUser', 'id': 1, 'role': 'admin'}

    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)

    assert user == {'username': 'testUser', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    encode = {'sub': 'testUser'}

    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exinfo:
        await get_current_user(token=token)

    assert exinfo.value.status_code == 401
    assert exinfo.value.detail == 'Could not validate user.'
