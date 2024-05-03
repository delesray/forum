from fastapi import APIRouter, HTTPException
from common.oauth import OptionalUser
from data.models import AnonymousUser, Category
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
def get_category_by_id(category_id: int, current_user: OptionalUser):
    category: Category = categories_services.get_by_id(category_id)
    if not category:
        raise HTTPException(404, 'No such category')
    
    if not category.is_private:
        topics = categories_services.get_topics_title_by_cat_id(category_id)
        return category, topics if topics else 'No topics'
    
    if isinstance(current_user, AnonymousUser):
        raise HTTPException(401, 'Login to view private categories')
