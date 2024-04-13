from fastapi import APIRouter
from data.models import User
from services import users_services

users_router = APIRouter(prefix='/users')


@users_router.get('/')
def get_all():
    users = users_services.get_all()
    return users


@users_router.get('/{id}')
def get_user_by_id(id: int):
    user = users_services.get_by_id(id)
    return user


@users_router.post('/')
def create_order(user: User):
    # if not user.email == 'correct':
    #     return Response(status_code=400, content='')

    msg = users_services.register(user)
    return msg
