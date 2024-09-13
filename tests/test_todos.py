from fastapi import status
from fastapi.testclient import TestClient

from main import app
from models.models import Todos
from routers.utils import get_db, get_current_user

from tests.utils import TestingSessionLocal, override_get_current_user, override_get_db
from tests.utils import test_todo as test_todo_fixture

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

test_todo = test_todo_fixture


def test_read_all_authenticated(test_todo):
    response = client.get('/todos')
    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()) == 1

    assert response.json() == [{
        'complete': False,
        'priority': 5,
        'owner_id': 1,
        'title': 'Learn to code',
        'description': 'This is a fake todo to be used in tests',
        'id': 1
    }]


def test_read_one_authenticated(test_todo):
    response = client.get('/todos/todo/1')
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        'complete': False,
        'priority': 5,
        'owner_id': 1,
        'title': 'Learn to code',
        'description': 'This is a fake todo to be used in tests',
        'id': 1
    }


def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todos/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {
        'detail': 'ToDo not found.'
    }


def test_create_todo(test_todo):
    request_data = {
        'title': 'New ToDo Created',
        'description': 'This is a ToDo to test the creation route',
        'priority': 3,
        'complete': True
    }

    response = client.post('/todos/todo', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.title == 'New ToDo Created').first()

    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
    assert model.id == 2


def test_update_todo(test_todo):
    request_data = {
        'title': 'ToDo title updated',
        'description': 'This ToDo was updated by put method',
        'priority': 1,
        'complete': True
    }

    response = client.put('/todos/todo/1', json=request_data)

    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'ToDo title updated',
        'description': 'This ToDo was updated by put method',
        'priority': 1,
        'complete': True
    }

    response = client.put('/todos/todo/999', json=request_data)

    assert response.status_code == 404
    assert response.json() == {'detail': 'ToDo not found.'}


def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).all()

    assert model == []


def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/999')
    assert response.status_code == 404
