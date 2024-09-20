from fastapi import Depends, status
from fastapi import FastAPI, Request
from models.models import Base
from database.config import engine
from routers import admin, auth, todos, users
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from routers.utils import db_dependency, get_current_user


app = FastAPI(docs_url=None, redoc_url=None)


@app.get('/healthy')
async def health_check():
    return {'status': 'Healthy'}

Base.metadata.create_all(bind=engine)

app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get('/')
def test(request: Request):
    return RedirectResponse(
        url='/todos/todo-page',
        status_code=status.HTTP_302_FOUND)


@app.get("/docs")
async def get_documentation(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return todos.redirect_to_login()
    except:
        return todos.redirect_to_login()

    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
