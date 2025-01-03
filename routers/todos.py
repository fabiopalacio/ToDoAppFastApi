from typing import Optional
from fastapi import APIRouter, HTTPException, Path, Request, status
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

from pydantic import BaseModel, Field

from models.models import Todos
from routers.utils import TodosCompleteUpdate, db_dependency, get_current_user, user_dependecy

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/todos',
    tags=['todos']

)


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(max_length=100)
    priority: int = Field(ge=0, le=5)
    complete: bool


def redirect_to_login():
    redirect_response = RedirectResponse(
        url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie('access_token')
    return redirect_response


# PAGES


@router.get('/todo-page')
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todos = await read_all(user, db)

        completed = 0
        incompleted = 0

        for todo in todos:
            if todo.complete:
                completed = completed+1
            else:
                incompleted = incompleted + 1

        return templates.TemplateResponse(
            'todo.html',
            {
                'request': request,
                'todos': todos,
                'user': user,
                'completed': completed,
                'incompleted': incompleted
            }
        )
    except:
        return redirect_to_login()


@router.get('/add-todo-page')
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse(
            'add-todo.html',
            {
                'request': request,
                'user': user
            }
        )
    except:
        return redirect_to_login()


@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todo = await read_todo(user, db, todo_id)

        return templates.TemplateResponse(
            'edit-todo.html',
            {
                'request': request,
                'user': user,
                'todo': todo
            }
        )
    except:
        return redirect_to_login()

# ENDPOINTS


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependecy, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).order_by(Todos.complete, Todos.priority.desc()).all()


@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(
        user: user_dependecy,
        db: db_dependency,
        todo_id: int = Path(ge=0)):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).\
        filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ToDo not found.')


@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(
        user: user_dependecy,
        db: db_dependency,
        todo_request: TodoRequest):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)

    db.commit()


@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependecy,
        db: db_dependency,
        todo_request: TodoRequest,
        todo_id: int = Path(ge=0)):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(
        Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ToDo not found.')

    else:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.add(todo_model)
        db.commit()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        user: user_dependecy,
        db: db_dependency,
        todo_id: int = Path(ge=0)):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(
        Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='ToDo not found.')

    db.delete(todo_model)
    db.commit()


@router.delete('/delete_completed_todos', status_code=status.HTTP_204_NO_CONTENT)
async def delete_in_batch(
        user: user_dependecy,
        db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(
        Todos.complete == 'true').all()
    print(todos)
    for todo in todos:
        db.delete(todo)

    db.commit()


@router.patch('/finish_todos', status_code=status.HTTP_204_NO_CONTENT)
async def update_in_batch(
        user: user_dependecy,
        db: db_dependency,
        todos_id: TodosCompleteUpdate):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')
    for item in todos_id.todos_id:
        todo = db.query(Todos).filter(Todos.id == item).filter(
            Todos.owner_id == user.get('id')).first()
        if todo:
            todo.complete = True
            db.add(todo)
    db.commit()
