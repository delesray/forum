from fastapi import APIRouter, Response
from data.models import User
from services import users_services

users_router = APIRouter(prefix='/users')


@users_router.get('/')
def get_all_users():
    users = users_services.get_all()
    return users


@users_router.get('/{id}')
def get_user_by_id(id: int):
    user = users_services.get_by_id(id)
    return user


@users_router.post('/')
def register_user(user: User):
    result, code = users_services.register(user)
    return Response(status_code=code, content=result)


@users_router.put('/{id}', status_code=200)
def update_user(id: int, user: User):
    existing_user = users_services.get_by_id(id)
    if not existing_user:
        return Response(status_code=404, content=f"User with id:{id} does\'t exist!")

    result, code = users_services.update(existing_user, user)
    return result

# @users_router.delete('/{id}', status_code=204)
# def delete_user_by_id(id: int):
#     existing_user =  users_services.get_by_id(id)
#     if not existing_user:
#         return Response(status_code=404, content=f"User with id:{id} does\'t exist!")
#
#     users_services.delete(existing_user)
