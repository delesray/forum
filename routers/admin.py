from fastapi import APIRouter, Header
from data.models import Category
from services import categories_services, users_services
from common.auth import is_admin_or_raise_401_403, UserAuthDep
from common.responses import BadRequest, Forbidden, Unauthorized, Created
from views import category_view

admin_router = APIRouter(prefix='/admin', tags=['admin'])


# ============================== Categories ==============================

@admin_router.post('/categories', status_code=201)
def create_category(category: Category, existing_user: UserAuthDep):
    if not existing_user.is_admin:  # todo dependency
        return Forbidden()

    result = categories_services.create(category)
    if isinstance(result, Category):
        return result
    return BadRequest(result.msg)


@admin_router.patch('/categories/{category_id}/privacy', status_code=202)
def switch_category_privacy(category_id: int, existing_user: UserAuthDep):
    if not existing_user.is_admin:  # todo dependancy
        return Forbidden()

    category = categories_services.get_by_id(category_id)
    if not category:
        return BadRequest("No such category")

    categories_services.update_privacy(not category.is_private, category_id)
    return f'Category {category.name} is {'public' if category.is_private else 'private'} now'


@admin_router.patch('/categories/{category_id}/locking', status_code=202)
def switch_category_locking(category_id: int, existing_user: UserAuthDep):
    if not existing_user.is_admin:
        return Forbidden()

    category = categories_services.get_by_id(category_id)
    if not category:
        return BadRequest("No such category")

    categories_services.update_locking(not category.is_locked, category_id)
    return f'Category {category.name} is {'unlocked' if category.is_locked else 'locked'} now'


# ============================== Users ==============================

@admin_router.post('/users/{user_id}/categories/{category_id}')
def give_user_category_read_access(user_id: int, category_id: int, existing_user: UserAuthDep):
    if not existing_user.is_admin:
        return Forbidden()
    if not users_services.get_by_id(user_id):
        return BadRequest('No such user')
    if not categories_services.get_by_id(category_id):
        return BadRequest('No such category')

    if categories_services.is_user_in(user_id, category_id):
        return BadRequest('User is already in the category')

    categories_services.add_user(user_id, category_id)
    return 'User successfully added to that category and he can read'


@admin_router.delete('/users/{user_id}/categories/{category_id}')
def revoke_user_category_read_access(user_id: int, category_id: int, existing_user: UserAuthDep):
    if not existing_user.is_admin:
        return Forbidden()
    if not users_services.get_by_id(user_id):
        return BadRequest('No such user')
    if not categories_services.get_by_id(category_id):
        return BadRequest('No such category')

    categories_services.remove_user(user_id, category_id)
    return 'User is not in that category anymore'


@admin_router.patch('/users/{user_id}/categories/{category_id}/access')
def switch_user_category_write_access(user_id: int, category_id: int, existing_user: UserAuthDep):
    if not existing_user.is_admin:
        return Forbidden()
    if not users_services.get_by_id(user_id):
        return BadRequest('No such user')
    if not categories_services.get_by_id(category_id):
        return BadRequest('No such category')

    access = categories_services.get_user_access_level(user_id, category_id)
    if access is None:
        return "User is not in that category"

    categories_services.update_user_access_level(user_id, category_id, not access)
    return f"User {'cannot' if access else 'can'} write"


@admin_router.get('/users/categories/{category_id}')
def view_privileged_users(category_id: int, existing_user: UserAuthDep):
    if not existing_user.is_admin:
        return Forbidden()

    category = categories_services.get_by_id(category_id)
    if not category:
        return BadRequest('No such category')
    elif not category.is_private:
        return BadRequest(f'{category.name} is public')

    users = categories_services.get_privileged_users(category_id)
    if not users:
        return "No users in that category"

    response = category_view.priviliged_users_view(category, users)
    return response


# ============================== Topics ==============================

@admin_router.patch('/topics/{topic_id}/locking')
def switch_topic_locking(topic_id: int, existing_user: UserAuthDep):
    pass
