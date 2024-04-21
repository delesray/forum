from fastapi import APIRouter, Header, Response
from data.models import User
from services import users_services
from data.models import LoginData
from common.responses import BadRequest
from common.auth import get_user_or_raise_401

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post('/login')
def login(data: LoginData):
    user = users_services.try_login(data.username, data.password)

    if user:
        token = users_services.create_token(user)
        return {'token': token}
    return BadRequest('Invalid login data')


@users_router.post('/register')
def register_user(user: User):
    result = users_services.register(user)
    if isinstance(result, int):
        return f"User with id: {result} registered"
    return BadRequest(result.msg)


@users_router.get('/')
def get_all_users():
    users = users_services.get_all()
    return users


@users_router.get('/{user_id}')
def get_user_by_id(user_id: int):
    user = users_services.get_by_id(user_id)
    if not user:
        return Response(status_code=404, content=f"User with id:{user_id} does\'t exist!")
    return user


@users_router.put('/', status_code=200)
def update_user(user: User, x_token: str = Header()):
    existing_user = get_user_or_raise_401(x_token)

    if not user:
        return BadRequest('Login required')

    result = users_services.update(existing_user, user)
    return result


@users_router.delete('/', status_code=204)
def delete_user_by_id(password: str, x_token: str = Header()):
    existing_user = get_user_or_raise_401(x_token)

    # pass should be hashed
    if existing_user.password != password:
        return BadRequest('Incorrect password')

    users_services.delete(existing_user.user_id)
