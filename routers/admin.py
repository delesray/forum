from fastapi import APIRouter, Header
from data.models import Category
from services import categories_services, users_services
from common.auth import is_admin_or_raise_401_403, UserAuthDep2
from common.responses import BadRequest, Forbidden, Unauthorized, Created

admin_router = APIRouter(prefix='/admin', tags=['admin'])


@admin_router.post('/categories', status_code=201)
def create_category(category: Category, existing_user: UserAuthDep2):
    if not existing_user:  # todo dependency
        return Unauthorized()

    if not existing_user.is_admin:  # todo dependency
        return Forbidden()

    result = categories_services.create(category)
    if isinstance(result, Category):
        return result
    return BadRequest(result.msg)


# todo test one more time
@admin_router.patch('/categories/{category_id}/privacy', status_code=202)
def switch_category_privacy(category_id: int, existing_user: UserAuthDep2):
    if not existing_user.is_admin:  # todo dependancy
        return Forbidden()

    category = categories_services.get_by_id(category_id)
    if not category:
        return BadRequest("No such category")

    if category.is_private:
        categories_services.publicize(category_id)
        return f'Category {category.name} is public now'
    else:
        categories_services.privatize(category_id)
        return f'Category {category.name} is private now'


@admin_router.patch('/categories/{category_id}/locking', status_code=202)
def switch_category_locking(category_id: int, existing_user: UserAuthDep2):
    if not existing_user.is_admin:
        return Forbidden

    category = categories_services.get_by_id(category_id)
    if not category:
        return BadRequest("No such category")

    if category.is_locked:
        categories_services.unlock(category_id)
        return f'Category {category.name} is unlocked now'
    else:
        categories_services.lock(category_id)
        return f'Category {category.name} is locked now'


@admin_router.post('/users/{user_id}/categories/{category_id}', status_code=201)
def give_user_a_category_read_access(user_id: int, category_id: int, existing_user: UserAuthDep2):
    if not existing_user.is_admin:
        return Forbidden

    if not users_services.get_by_id(user_id):
        return BadRequest('No such user')

    if not categories_services.get_by_id(category_id):
        return BadRequest('No such category')

    if categories_services.is_user_in(user_id, category_id):
        return BadRequest('User is already in the category')

    categories_services.add_user(user_id, category_id)
    return 'User successfully added to that category'


@admin_router.delete('/users/{user_id}/categories/{category_id}')
def revoke_user_category_read_access():
    pass


@admin_router.patch('/users/{user_id}/categories/{category_id}/access/{boolean}', status_code=201)
def give_user_a_category_write_access():
    pass
#
# @admin_router.patch('/users/{user_id}/categories/{category_id}', status_code=201)
# def revoke_user_category_write_access():
#     pass