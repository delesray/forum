from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from data.models import User, TokenData, UserRegister, UserUpdate
from services import users_services
from common.oauth import create_access_token, UserAuthDep
from common.utils import verify_password
from typing import Annotated


users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post('/register')
def register_user(user: UserRegister):
    # todo catch username and pass validation errors from Pydantic
    result = users_services.register(user)

    if not isinstance(result, int):
        raise HTTPException(status_code=400, detail=result.msg)
        
    return f"User with ID: {result} registered"


@users_router.post('/login')
# now login works through Swagger docs but use form data in Postman
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


@users_router.get('/')
def get_all_users():
    users = users_services.get_all()
    return users


@users_router.get('/{user_id}')
def get_user_by_id(user_id: int, existing_user: UserAuthDep):
    user = users_services.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID: {user_id} does\'t exist!")
    return user

# todo - patch request to update user pass, UserUpdatePassword model

@users_router.put('/')
def update_user(user: UserUpdate, existing_user: UserAuthDep):
    
    if user.username != existing_user.username:
        raise HTTPException(status_code=403, detail=f"Only admins can edit other users' data")

    result = users_services.update(existing_user, user)
    return result


# todo flag deleted in db, don't delete
@users_router.delete('/', status_code=204)
def delete_user_by_id(password: dict, existing_user: UserAuthDep):

    if not verify_password(password['password'], existing_user.password):
        raise HTTPException(status_code=400, detail=f"Incorrect password")

    users_services.delete(existing_user.user_id)
