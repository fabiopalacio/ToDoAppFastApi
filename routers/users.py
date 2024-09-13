from fastapi import APIRouter, HTTPException, status
from models.models import Users

from routers.utils import db_dependency, user_dependecy, UserRequest, UserVerificatin, bcrypt_context

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get('', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependecy, db: db_dependency):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    my_user = db.query(Users).filter(Users.id == user.get('id')).first()

    if my_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found.')

    return my_user


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
        user: user_dependecy,
        db: db_dependency,
        user_verification: UserVerificatin):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(
            user_verification.password,
            user_model.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(
        user_verification.new_password)

    db.add(user_model)
    db.commit()


@router.put('/update', status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
        user: user_dependecy,
        db: db_dependency,
        user_request: UserRequest):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user.')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if hasattr(user_request, 'phone_number'):
        user_model.phone_number = user_request.phone_number

    if hasattr(user_request, 'first_name'):
        user_model.first_name = user_request.first_name

    if hasattr(user_request, 'last_name'):
        user_model.last_name = user_request.last_name

    if hasattr(user_request, 'email'):
        user_model.email = user_request.email

    db.add(user_model)
    db.commit()
