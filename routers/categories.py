from fastapi import APIRouter, Response
from data.models import Category
from services import categories_services

categories_router = APIRouter(prefix='/categories')


@categories_router.get('/')
def get_all_categories():
    categories = categories_services.get_all()
    return categories


@categories_router.get('/{id}')
def get_category_by_id(id: int):
    category = categories_services.get_by_id(id)
    return category


@categories_router.post('/')
def create_category(category: Category):
    result, code = categories_services.create(category)
    return Response(status_code=code, content=result)


@categories_router.put('/{id}', status_code=200)
def update_category(id: int, category: Category):
    existing_category = categories_services.get_by_id(id)
    if not existing_category:
        return Response(status_code=404, content=f"Category with id:{id} does\'t exist!")

    result, code = categories_services.update(existing_category, category)
    return result

# @categories_router.delete('/{id}', status_code=204)
# def delete_category_by_id(id: int):
#     existing_user =  categories_services.get_by_id(id)
#     if not existing_user:
#         return Response(status_code=404, content=f"Category with id:{id} does\'t exist!")
#
#     users_services.delete(existing_user)
