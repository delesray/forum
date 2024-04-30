from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from data.models import TokenData, UserRegister, UserUpdate, UserUpdatePassword
from services import users_services
from common.oauth import create_access_token, UserAuthDep
from common.utils import verify_password
from typing import Annotated
from common.utils import verify_password

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
def get_user_by_id(user_id: int, existing_user: UserAuthDep):
    user = users_services.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID: {user_id} does\'t exist!")
    return user


@users_router.put('/', status_code=200)
def update_user(user: UserUpdate, existing_user: UserAuthDep):
    result = users_services.update(existing_user, user)
    return result


@users_router.patch('/password', status_code=200)
def update_user_password(passwords: UserUpdatePassword, existing_user: UserAuthDep):
    if not verify_password(passwords.old, existing_user.password):
        return HTTPException(status_code=401, detail="Old password does not match the current one")
    if not passwords.new == passwords.re_new:
        return HTTPException(status_code=401, detail="New password does not match the repeat password")


# todo flag deleted in db, don't delete
@users_router.delete('/', status_code=204)
def delete_user_by_id(password: dict, existing_user: UserAuthDep):
    if not verify_password(password['password'], existing_user.password):
        raise HTTPException(status_code=400, detail=f"Incorrect password")

    users_services.delete(existing_user.user_id)
