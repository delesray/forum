from fastapi import APIRouter, Body, HTTPException, Query

from services import topics_services, categories_services
from common.oauth import OptionalUser, UserAuthDep
from common.responses import BadRequest, NotFound, Forbidden
from data.models.topic import Status, TopicUpdate, TopicCreate, TopicsPaginate
from data.models.user import AnonymousUser
from common import utils

# from fastapi_pagination import paginate
# from fastapi_pagination.links import Page
from starlette.requests import Request

topics_router = APIRouter(prefix='/topics', tags=['topics'])


@topics_router.get('/')
def get_all_topics(
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(2, ge=1, le=10, description="Page size"),
        sort: str | None = None,
        sort_by: str = 'topic_id',
        search: str | None = None,
        username: str | None = None,
        category: str | None = None,
        status: str | None = None
):
    topics = topics_services.get_all(
        page=page, size=size, sort=sort, sort_by=sort_by, search=search,
        username=username, category=category, status=status)
    if not topics:
        return []

    total_topics = topics_services.get_total_count()
    pagination_info = utils.get_pagination_info(total_topics, page, size)

    links = utils.create_links(request, pagination_info)

    return TopicsPaginate(
        topics=topics,
        pagination_info=pagination_info,
        links=links
    )


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int, current_user: OptionalUser):
    current = topics_services.get_topic_by_id_with_replies(topic_id)

    if not current:
        raise HTTPException(
            status_code=404,
            detail=f"Topic #ID:{topic_id} does not exist"
        )

    category = categories_services.get_by_id(current.topic.category_id)

    if not category.is_private:
        return current

    # Verify category privacy
    if isinstance(current_user, AnonymousUser):
        raise HTTPException(
            status_code=401,
            detail='Login to view topics in private categories'
        )

    if not current_user.is_admin and not categories_services.has_access_to_private_category(current_user.user_id,
                                                                                            category.category_id):
        raise HTTPException(
            status_code=403,
            detail=f'You do not have permission to access this private category'
        )

    return current


@topics_router.post('/')
def create_topic(new_topic: TopicCreate, current_user: UserAuthDep):
    category = categories_services.get_by_id(new_topic.category_id)

    if not category:
        return NotFound(f'Category #ID: {new_topic.category_id} does not exist')

    if category.is_locked:
        return Forbidden(f'Category #ID: {category.category_id}, Name: {category.name} is locked')

    if category.is_private:
        if categories_services.has_write_access(current_user.user_id, category.category_id):
            result = topics_services.create(new_topic, current_user)
        else:
            return Forbidden(f"You do not have permission to post in this private category")

    result = topics_services.create(new_topic, current_user)

    if isinstance(result, int):
        return f'Topic {result} was successfully created!'
    return BadRequest(result)


@topics_router.patch('/{topic_id}/best-reply')
def update_topic_best_reply(topic_id: int, current_user: UserAuthDep, topic_update: TopicUpdate = Body(...)):
    if not topic_update.best_reply_id:
        return BadRequest(f"Data not provided to make changes")

    error_response = topics_services.validate_topic_access(topic_id, current_user)
    if error_response:
        return error_response

    topic_replies_ids = topics_services.get_topic_replies(topic_id)

    if not topic_replies_ids:
        return NotFound(f"Topic with id:{topic_id} does not have replies")

    if topic_update.best_reply_id in topic_replies_ids:
        return topics_services.update_best_reply(topic_id, topic_update.best_reply_id)

    else:
        return BadRequest("Invalid reply ID")


@topics_router.patch('/{topic_id}/locking')
def switch_topic_locking(topic_id: int, existing_user: UserAuthDep):
    topic = topics_services.get_by_id(topic_id)
    if not topic:
        return BadRequest("No such topic")

    if topic.user_id != existing_user.user_id:
        return Forbidden()
    topics_services.update_locking(not Status.str_int[topic.status], topic_id)
    return f'Topic {topic.title} is {Status.opposite[topic.status]} now'
