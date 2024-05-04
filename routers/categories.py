from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Query
from common.oauth import OptionalUser
from data.models.user import AnonymousUser
from data.models.category import Category, CategoryTopicsPaginate, CategoryWithTopics
from services import categories_services
from common.utils import get_pagination_info, create_links
# from fastapi_pagination.links import Page
# from fastapi_pagination import paginate


categories_router = APIRouter(prefix='/categories', tags=['categories'])


@categories_router.get('/')
def get_all_categories(
        request: Request,
        sort: str | None = None,
        search: str | None = None) -> list[Category]:
    
    # sort works in-memory - okay for low number of categories
    if sort and (sort.lower() in ('asc', 'desc')):
        return sorted(categories_services.get_all(search=search),
                      key=lambda x: x.name, reverse=sort == 'desc')

    return categories_services.get_all(search=search)


@categories_router.get('/{category_id}')
def get_category_by_id(
        category_id: int,
        current_user: OptionalUser,
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(2, ge=1, le=10, description="Page size"),
        sort: str | None = None,
        search: str | None = None) -> CategoryTopicsPaginate:
    
    """
    1. Returns Category with a list of Topics, if Category is public
    2. If Category is private requires authentication
    3. Topics in a Category can be searched by title or sorted by title in alphabetical order (asc / desc)
    """

    category = categories_services.get_cat_by_id_with_topics(
        category_id=category_id, search=search, sort=sort, page=page, size=size)

    if not category:
        raise HTTPException(404, 'Category not found')

    if category.is_private:
        if isinstance(current_user, AnonymousUser):
            raise HTTPException(401, 'Login to view private categories')

        if not current_user.is_admin and not categories_services.has_access_to_private_category(current_user.user_id,
                                                                  category.category_id):
            raise HTTPException(
                status_code=403,
                detail=f'You do not have permission to access this private category'
            )
        
    total_topics_in_cat = len(category.topics)
    pagination_info = get_pagination_info(total_topics_in_cat, page, size)

    links = create_links(request, pagination_info)

    return CategoryTopicsPaginate(
        category=category,
        pagination_info=pagination_info,
        links=links
    )

