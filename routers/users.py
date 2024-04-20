from fastapi import APIRouter, Response
from data.models import User
from services import users_services
from data.models import LoginData
from common.responses import BadRequest

users_router = APIRouter(prefix='/users')


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


@users_router.post('/register')
def register_user(user: User):
    result = users_services.register(user)
    if isinstance(result, int):
        return f"User with id: {result} registered"
    return BadRequest(result.msg)
g

@users_router.post('/login')
def login(data: LoginData):
    user = users_services.try_login(data.username, data.password)

    if user:
        token = users_services.create_token(user)
        return {'token': token}
    return BadRequest('Invalid login data')


@users_router.put('/{user_id}', status_code=200)
def update_user(user_id: int, user: User):
    existing_user = users_services.get_by_id(user_id)
    if not existing_user:
        return Response(status_code=404, content=f"User with id:{user_id} does\'t exist!")

    result, code = users_services.update(existing_user, user)
    return result

# @users_router.delete('/{user_id}', status_code=204)
# def delete_user_by_id(id: int):
#     existing_user =  users_services.get_by_id(id)
#     if not existing_user:
#         return Response(status_code=404, content=f"User with id:{id} does\'t exist!")
#
#     users_services.delete(existing_user)
