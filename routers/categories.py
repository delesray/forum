from fastapi import APIRouter, HTTPException
from common.oauth import OptionalUser
from data.models.user import AnonymousUser
from data.models.category import Category, CategoryWithTopics
from services import categories_services
# from fastapi_pagination.links import Page
# from fastapi_pagination import paginate

categories_router = APIRouter(prefix='/categories', tags=['categories'])


@categories_router.get('/')
def get_all_categories(
        sort: str | None = None,
        search: str | None = None) -> list[Category]:
    
    if sort:
        return sorted(categories_services.get_all(search=search),
                               key=lambda x: x.name, reverse=sort == 'desc')

    return categories_services.get_all(search=search)


@categories_router.get('/{category_id}')
def get_category_by_id(
    category_id: int, 
    current_user: OptionalUser,
    sort: str | None = None,
    search: str | None = None):

    category: Category = categories_services.get_by_id(category_id)
    if not category:
        raise HTTPException(404, 'No such category')

    if category.is_private:
        topics = categories_services.get_topics_by_cat_id(category_id)
        return category, topics if topics else 'No topics'

    if isinstance(current_user, AnonymousUser):
        raise HTTPException(401, 'Login to view private categories')
    
    if not categories_services.has_access_to_private_category(current_user.user_id, 
                                                              category.category_id):
        raise HTTPException(
            status_code=403,
            detail=f'You do not have permission to access this private category'
        )

    topics = categories_services.get_topics_by_cat_id(category_id)
    return category, topics if topics else 'No topics'
