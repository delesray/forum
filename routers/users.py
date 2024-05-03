from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from data.models.user import UserRegister, UserUpdate, UserChangePassword, UserDelete, TokenData
from services import users_services
from common.oauth import create_access_token, UserAuthDep
from common.utils import verify_password
from typing import Annotated
from common import utils

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post('/register', status_code=201)
def register_user(user: UserRegister):
    # todo catch username and pass validation errors from Pydantic
    result = users_services.register(user)

    if not isinstance(result, int):
        raise HTTPException(status_code=400, detail=result.msg)

    return f"User with ID: {result} registered"


# now login works through Swagger docs but use form data in Postman
@users_router.post('/login', status_code=200)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users_services.try_login(form_data.username, form_data.password)

    # to display the error in Swagger - HTTPException
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(TokenData(username=user.username, is_admin=user.is_admin))
    return token


@users_router.get('/', status_code=200)
def get_all_users():
    users = users_services.get_all()
    return users


@users_router.get('/{user_id}', status_code=200)
def get_user_by_id(user_id: int):
    user = users_services.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID: {user_id} does\'t exist!")
    return user


@users_router.put('/', status_code=200)
def update_user(user: UserUpdate, existing_user: UserAuthDep):
    result = users_services.update(existing_user, user)
    return result


@users_router.patch('/password', status_code=200)
def change_user_password(data: UserChangePassword, existing_user: UserAuthDep):
    """
    1. Verifies the current password
    2. Verifies the new password match
    3. Updates in db with new_hashed_password
    """
    if not utils.verify_password(data.current_password, existing_user.password):
        return HTTPException(401, "Current password does not match")
    if not data.new_password == data.confirm_password:
        return HTTPException(401, "New password does not match")

    new_hashed_password = utils.hash_pass(data.new_password)
    users_services.change_password(existing_user.user_id, new_hashed_password)
    return 'Password changed successfully'


@users_router.delete('/', status_code=204)
def delete_user_by_id(existing_user: UserAuthDep, body: UserDelete):
    """
    1. Verifies the current password
    2. Flags the user as deleted in db
        2.1 Triggers an object in db that deletes his messages
    """
    if not verify_password(body.current_password, existing_user.password):
        raise HTTPException(status_code=400, detail=f"Current password does not match")

    users_services.delete(existing_user.user_id)