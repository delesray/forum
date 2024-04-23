from fastapi import APIRouter, Response
from data.models import Category
from services import categories_services

categories_router = APIRouter(prefix='/categories', tags=['categories'])


@categories_router.get('/')
def get_all_categories():
    categories = categories_services.get_all()
    return categories


@categories_router.get('/{category_id}')
def get_category_by_id(category_id: int):
    category = categories_services.get_by_id(category_id)
    if not category:
        return Response(status_code=404, content=f"Category with id:{category_id} does\'t exist!")
    return category



@categories_router.put('/{category_id}', status_code=200)
def update_category(category_id: int, category: Category):
    existing_category = categories_services.get_by_id(category_id)
    if not existing_category:
        return Response(status_code=404, content=f"Category with id:{category_id} does\'t exist!")

    result, code = categories_services.update(existing_category, category)
    return result

# @categories_router.delete('/{category_id}', status_code=204)
# def delete_category_by_id(category_id: int):
#     existing_user =  categories_services.get_by_id(id)
#     if not existing_user:
#         return Response(status_code=404, content=f"Category with id:{id} does\'t exist!")
#
#     users_services.delete(existing_user)
