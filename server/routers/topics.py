from fastapi import APIRouter, Body, HTTPException, Query
from services import topics_services, categories_services, users_services, replies_services
from common.oauth import OptionalUser, UserAuthDep
from common.responses import SC
from data.models.topic import Status, TopicUpdate, TopicCreate, TopicsPaginate, TopicRepliesPaginate
from data.models.user import AnonymousUser
from common.utils import Page
from starlette.requests import Request

topics_router = APIRouter(prefix='/topics', tags=['topics'])


@topics_router.get('/')
def get_all_topics(
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(Page.SIZE, ge=1, le=15, description="Page size"),
        sort: str | None = None,
        sort_by: str = 'topic_id',
        search: str | None = None,
        username: str | None = None,
        category: str | None = None,
        status: str | None = None
):
    
    """
    - User can view all Topics
    - Topics can be sorted by:
        - topic_id
        - title 
        - user_id of the author
        - status (open or locked)
        - best_reply_id
        - category_id
    - Topics can be searched by:
        - title
        - username (of the author)
        - category name
        - status (open or locked)
    - User can choose number of pages displayed (1 by default) and number of items per page (1 by default, maximum 15)
    """

    if username and not users_services.exists_by_username(username):
        raise HTTPException(
            status_code=SC.NotFound,
            detail=f"User not found"
        )

    if category and not categories_services.exists_by_name(category):
        raise HTTPException(
            status_code=SC.NotFound,
            detail=f"Category not found"
        )

    if status and status.lower() not in [Status.OPEN, Status.LOCKED]:
        raise HTTPException(
            status_code=SC.BadRequest,
            detail=f"Invalid status value"
        )

    if sort and sort.lower() not in ['asc', 'desc']:
        raise HTTPException(
            status_code=SC.BadRequest,
            detail=f"Invalid sort parameter"
        )

    if sort_by and sort_by.lower() not in ['topic_id', 'title', 'user_id', 'status', 'best_reply_id', 'category_id']:
        raise HTTPException(
            status_code=SC.BadRequest,
            detail=f"Invalid sort_by parameter"
        )

    topics, pagination_info, links = topics_services.get_topics_paginate_links(
              request=request, page=page, size=size, sort=sort, sort_by=sort_by,
              search=search, username=username, category=category, status=status
    )
    
    if not topics:
        return []

    return TopicsPaginate(
        topics=topics,
        pagination_info=pagination_info,
        links=links
    )


@topics_router.get('/{topic_id}')
def get_topic_by_id(
        topic_id: int, 
        current_user: OptionalUser,
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(Page.SIZE, ge=1, le=15, description="Page size")
) -> TopicRepliesPaginate:
    
    """
    - A guest can view a Topic with all of its Replies, if the Topic belongs to a public Category
    - If the Category is private, authentication is required
    """
    
    topic = topics_services.get_by_id(topic_id)

    if not topic:
        raise HTTPException(
            status_code=SC.NotFound,
            detail=f"Topic #ID:{topic_id} does not exist"
        )

    category = categories_services.get_by_id(topic.category_id)
    
    if category.is_private:
        
        if isinstance(current_user, AnonymousUser):
            raise HTTPException(
                status_code=SC.Unauthorized,
                detail='Login to view topics in private categories'
           )

        if not current_user.is_admin and not categories_services.has_access_to_private_category(current_user.user_id,
                                                                                            category.category_id):
            raise HTTPException(
                status_code=SC.Forbidden,
                detail=f'You do not have permission to access this private category'
            )
    
    replies, pagination_info, links = replies_services.get_all(topic_id=topic.topic_id, request=request, page=page, size=size)

    result = TopicRepliesPaginate(
        topic=topic, replies=replies, pagination_info=pagination_info, links=links)

    return result


@topics_router.post('/')
def create_topic(new_topic: TopicCreate, current_user: UserAuthDep):

    """
    - User can create a Topic, if the User has write access to the designated Category
    """
        
    category = categories_services.get_by_id(new_topic.category_id)

    if not category:
        raise HTTPException(SC.NotFound, f'Category #ID:{new_topic.category_id} does not exist')

    if category.is_locked:
        raise HTTPException(SC.Forbidden, f'Category #ID:{category.category_id}, Name: {category.name} is locked')

    if category.is_private:
        if categories_services.has_write_access(current_user.user_id, category.category_id):
            result = topics_services.create(new_topic, current_user)
        else:
            raise HTTPException(SC.Forbidden, f"You do not have permission to post in this private category")

    result = topics_services.create(new_topic, current_user.user_id)

    if isinstance(result, int):
        return f'Topic {result} was successfully created!'
    raise HTTPException(SC.BadRequest, result)


@topics_router.patch('/{topic_id}/bestReply')
def update_topic_best_reply(topic_id: int, current_user: UserAuthDep, topic_update: TopicUpdate = Body(...)):
    
    """
    - User can choose a best Reply to a Topic, if the User owns the Topic
    """

    if not topic_update.best_reply_id:
        raise HTTPException(SC.BadRequest, f"Data not provided to make changes")

    error_response = topics_services.validate_topic_access(topic_id, current_user)
    if error_response:
        return error_response

    topic_replies_ids = topics_services.get_topic_replies(topic_id)

    if not topic_replies_ids:
        raise HTTPException(SC.NotFound, f"Topic with id:{topic_id} does not have replies")

    if topic_update.best_reply_id in topic_replies_ids:
        return topics_services.update_best_reply(topic_id, topic_update.best_reply_id)

    else:
        raise HTTPException(SC.BadRequest, "Invalid REPLY ID")


@topics_router.patch('/{topic_id}/locking')
def switch_topic_locking(topic_id: int, existing_user: UserAuthDep):
    
    """
    - User can lock or unlock a Topic, if the User owns the Topic
    """
    return switch_topic_locking_helper(topic_id, existing_user)


def switch_topic_locking_helper(topic_id, user):
    topic = topics_services.get_by_id(topic_id)
    if not topic:
        raise HTTPException(SC.BadRequest, "No such topic")

    if not user.is_admin and topic.user_id != user.user_id:  # if user doesn't own topic
        raise HTTPException(SC.BadRequest, 'You must be admin or owner to switch locking')

    topics_services.update_locking(not Status.str_int[topic.status], topic_id)
    return f'Topic {topic.title} is {Status.opposite[topic.status]} now'
