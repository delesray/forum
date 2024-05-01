from fastapi import APIRouter
from data.models import Category
from services import categories_services
from common.responses import BadRequest
from fastapi_pagination.links import Page
from fastapi_pagination import paginate


categories_router = APIRouter(prefix='/categories', tags=['categories'])


@categories_router.get('/')
def get_all_categories(
    sort: str | None = None,
    search: str | None = None) -> Page[Category]:

    if sort:
        return paginate(sorted(categories_services.get_all(search=search), 
                               key=lambda x: x.name, reverse=sort == 'desc'))
    
    return paginate(categories_services.get_all(search=search))


@categories_router.get('/{category_id}')
def get_category_by_id(category_id: int):
    category = categories_services.get_by_id(category_id)
    if not category:
        return BadRequest(f"No such category")

    topics = categories_services.get_topics_title_by_cat_id(category_id)

    return category, topics if topics else 'No topics'
