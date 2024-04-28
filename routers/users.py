from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from data.models import User, TokenData, RegisterUser
from services import users_services
from common.responses import BadRequest, Forbidden
from common.auth import create_access_token, get_current_user
from common.utils import verify_password
from typing import Annotated


users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post('/login')
# now login works through Swagger docs but use form data in Postman
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    user = users_services.try_login(form_data.username, form_data.password)
    
    # to display the error in Swagger - HTTPException
    if not user:
        return HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(TokenData(username=user.username, is_admin=user.is_admin))
    return token


@users_router.post('/register')
def register_user(user: RegisterUser):
    # todo catch username and pass validation errors
    result = users_services.register(user)

    if isinstance(result, int):
        return f"User with id: {result} registered"

    return BadRequest(result.msg)


@users_router.get('/')
def get_all_users():
    users = users_services.get_all()
    return users


# todo requires authentication ?
@users_router.get('/{user_id}')
def get_user_by_id(user_id: int):
    user = users_services.get_by_id(user_id)
    if not user:
        return Response(status_code=404, content=f"User with id:{user_id} does\'t exist!")
    return user


@users_router.put('/', response_model=User,
                  response_model_exclude={"password", "is_admin"})
def update_user(user: User, existing_user: Annotated[User, Depends(get_current_user)]):
    if user.username != existing_user.username:
        return Forbidden()  # only admin

    result = users_services.update(existing_user, user)
    return result


@users_router.delete('/', status_code=204)
def delete_user_by_id(password: dict, existing_user: Annotated[User, Depends(get_current_user)]):
    if not verify_password(password['password'], existing_user.password):
        return BadRequest('Incorrect password')

    users_services.delete(existing_user.user_id)
