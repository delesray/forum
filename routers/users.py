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
