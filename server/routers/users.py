from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from common.responses import SC
from data.models.user import UserRegister, UserUpdate, UserChangePassword, UserDelete, TokenData
from services import users_services
from common.oauth import create_access_token, UserAuthDep
from common.utils import verify_password
from typing import Annotated
from common import utils

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.post('/register', status_code=SC.Created)
def register_user(user: UserRegister):
    """
    - Registers the user, if:
        - username is at least 4 chars and is not already taken
        - password is at least 4 chars
        - email follows the example
    - First name and last name are not required upon registration
    """
    result = users_services.register(user)

    if not isinstance(result, int):
        raise HTTPException(status_code=SC.BadRequest, detail=result.msg)

    return f"User with ID: {result} registered"


@users_router.post('/login')
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    - Logs the user, if username and password are correct
    - Returns access Token
    """
    user = users_services.try_login(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=SC.Unauthorized,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        TokenData(username=user.username, is_admin=user.is_admin))
    return token


@users_router.get('/')
def get_all_users():
    users = users_services.get_all()
    return users


@users_router.get('/{user_id}')
def get_user_by_id(user_id: int):
    """
    - Returns a user by ID, if the user exists
    """
    user = users_services.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=SC.NotFound, detail=f"User with ID: {user_id} does\'t exist!")
    return user


@users_router.put('/')
def update_user(user: UserUpdate, existing_user: UserAuthDep):
    """
    - Updates first name and/or last name of the authenticated user
    """
    result = users_services.update(existing_user, user)
    return result


@users_router.patch('/password')
def change_user_password(data: UserChangePassword, existing_user: UserAuthDep):
    """
    1. Verifies the current password
    2. Verifies the new password match
    3. Updates in db with new_hashed_password
    """
    if not utils.verify_password(data.current_password, existing_user.password):
        raise HTTPException(SC.Unauthorized, "Current password does not match")
    if not data.current_password != data.new_password:
        raise HTTPException(SC.BadRequest, "New password must be different from current password")
    if not data.new_password == data.confirm_password:
        raise HTTPException(SC.Unauthorized, "New password does not match")

    new_hashed_password = utils.hash_pass(data.new_password)
    users_services.change_password(existing_user.user_id, new_hashed_password)
    return 'Password changed successfully'


@users_router.delete('/', status_code=SC.NoContent)
def delete_user_by_id(existing_user: UserAuthDep, body: UserDelete):
    """
    - Verifies the current password
    - Flags the user as deleted in db
        - Triggers an object in db that deletes his messages
    """
    if not utils.verify_password(body.current_password, existing_user.password):
        raise HTTPException(status_code=SC.BadRequest,
                            detail=f"Current password does not match")

    users_services.delete(existing_user.user_id)
