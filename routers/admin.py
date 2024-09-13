from fastapi import APIRouter,  HTTPException, status

from models.models import Todos

from routers.utils import db_dependency, user_dependecy

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependecy, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed.')
    return db.query(Todos).all()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependecy, db: db_dependency, todo_id: int):

    if user is None or user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication failed.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ToDo not found.')

    db.delete(todo_model)
    db.commit()
