
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


def test_admin_read_all_authenticate(test_todo_fixture):

    response = client.get('/admin/todo')

    assert response.status_code == 200

    assert response.json() == [{
        'title': 'Learn to code',
        'description': 'This is a fake todo to be used in tests',
        'priority': 5,
        'complete': False,
        'owner_id': 1,
        'id': 1
    }]


def test_admin_delete_todo(test_todo_fixture):
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is not None

    response = client.delete('/admin/todo/1')
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None


def test_admin_delete_todo_not_found(test_todo_fixture):
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 999).first()

    assert model is None

    response = client.delete('/admin/todo/999')
    assert response.status_code == 404

    assert response.json() == {'detail': 'ToDo not found.'}
