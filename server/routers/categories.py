from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Query
from common.oauth import OptionalUser
from common.responses import SC
from data.models.user import AnonymousUser
from data.models.category import Category, CategoryTopicsPaginate
from services import categories_services, topics_services
from common.utils import get_pagination_info, create_links, Page


categories_router = APIRouter(prefix='/categories', tags=['categories'])


@categories_router.get('/')
def get_all_categories(
        sort: str | None = None,
        search: str | None = None) -> list[Category]:

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
        size: int = Query(Page.SIZE, ge=1, le=15, description="Page size"),
        search: str | None = None,
        sort: str | None = None,
        sort_by: str = 'topic_id',
) -> CategoryTopicsPaginate:
    
    """
    1. Returns Category with a list of Topics, if Category is public
    2. If Category is private requires authentication
    3. Topics in a Category can be searched by title or sorted by title in alphabetical order (asc / desc)
    """

    category = categories_services.get_by_id(category_id)

    if not category:
        raise HTTPException(SC.NotFound, 'Category not found')

    if category.is_private:
        if isinstance(current_user, AnonymousUser):
            raise HTTPException(SC.Unauthorized, 'Login to view private categories')

        if not current_user.is_admin and not categories_services.has_access_to_private_category(
                current_user.user_id, category.category_id):
            raise HTTPException(
                status_code=SC.Forbidden,
                detail=f'You do not have permission to access this private category'
            )

    topics, total_topics = topics_services.get_all(
        page=page, size=size, sort=sort, sort_by=sort_by, search=search,
        category=category.name
    )
    pagination_info = get_pagination_info(total_topics, page, size)

    links = create_links(request, pagination_info)

    return CategoryTopicsPaginate(
        category=category,
        topics=topics,
        pagination_info=pagination_info,
        links=links
    )