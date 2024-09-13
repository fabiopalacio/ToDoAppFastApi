
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base
from models.models import Todos, Users

from routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'userForTest', 'id': 1, 'role': 'admin'}


@pytest.fixture
def test_todo():
    todo = Todos(
        title='Learn to code',
        description='This is a fake todo to be used in tests',
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        email='email@email.com',
        username='testUsername',
        first_name='First',
        last_name='Last',
        hashed_password=bcrypt_context.hash('1234'),
        is_active=True,
        role='admin',
        phone_number='1212341234'
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()
