from tests.utils import test_user as test_user_fixture
from fastapi import status
from fastapi.testclient import TestClient

from main import app
from tests.utils import override_get_current_user, override_get_db
from routers.utils import get_db, get_current_user, bcrypt_context


test_user = test_user_fixture

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_return_user(test_user):
    response = client.get('/users')

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get('email') == 'email@email.com'
    assert response.json().get('username') == 'testUsername'
    assert response.json().get('first_name') == 'First'
    assert response.json().get('last_name') == 'Last'
    assert response.json().get('is_active') is True
    assert response.json().get('role') == 'admin'
    assert response.json().get('phone_number') == '1212341234'
    assert bcrypt_context.verify(
        '1234', response.json().get('hashed_password'))


def test_change_password_success(test_user):
    response = client.put(
        '/users/password', json={"password": "1234", "new_password": "654321"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_fails(test_user):
    # invalid new password
    response = client.put(
        '/users/password', json={"password": "1234", "new_password": "4321"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # invalid current password
    response = client.put(
        '/users/password', json={"password": "12345", "new_password": "654321"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}


def test_update_user(test_user):
    response = client.put(
        '/users/update', json={'phone_number': '(99)8888-7777'})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Checking the change:
    response = client.get('/users')
    assert response.json().get('phone_number') == '(99)8888-7777'
