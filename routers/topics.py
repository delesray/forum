from typing import Annotated
from fastapi import APIRouter, Response, Body, HTTPException, Header
from services import topics_services, categories_services
from common.responses import BadRequest, NotFound, Forbidden
from common.auth import UserAuthDep
from data.models import TopicUpdate, TopicCreate, Status
from starlette.requests import Request
from common.auth import get_current_user
from data.models import Topic

topics_router = APIRouter(prefix='/topics', tags=['topics'])


#TODO pagination for the get_all_topics endpoint to be implemented

@topics_router.get('/')
def get_all_topics(
        request: Request,
        sort: str | None = None,
        sort_by: str = 'topic_id',
        search: str | None = None,
        username: str | None = None,
        category: str | None = None,
        status: str | None = None
):
    authorization = request.headers.get("Authorization")  # get content from Authorization header from request

    if not authorization:
        topics = topics_services.get_all(search=search, username=username, category=category, status=status)
        if not topics:
            return []
        if sort and (sort == 'asc' or sort == 'desc'):
            return topics_services.custom_sort(topics, attribute=sort_by, reverse=sort == 'desc')
        else:
            return topics
    else:
        scheme, _, param = authorization.partition(" ")  # split and get token from param
        if (scheme.lower() != "bearer"):
            return Response(status_code=401, content=f"Not Authenticated")
        current_user = get_current_user(param)
        private_topics = topics_services.get_topics_from_private_categories(current_user)
        if not private_topics:
            return topics
        if sort and (sort == 'asc' or sort == 'desc'):
            return topics_services.custom_sort(private_topics, attribute=sort_by, reverse=sort == 'desc')
        else:
            return topics.extend(private_topics)


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int, x_token: Annotated[str | None, Header()] = None):
    topic = topics_services.get_by_id_cat_id(topic_id)
    if not topic:
        return NotFound()
    category = categories_services.get_by_id(topic.category_id)

    if not category.is_private:
        return topic

    # todo
    user = get_current_user(x_token)
    if not categories_services.is_user_in(user.id, category.category_id):
        return Forbidden()

    return topic

    # if category.is_private:
    #     user = UserAuthDep
    #     if user.
    # return topic


# @topics_router.get('/{topic_id}')
# def get_topic_by_id(request: Request, topic_id: int):
#
#     topic = topics_services.get_by_id(topic_id)
#     if not topic:
#         return Response(status_code=404, content=f"Topic with id:{topic_id} does not exist")
#
#     category = topics_services.get_category_by_name(topic.category)
#
#     if not category.is_private:
#         return topics_services.topic_with_replies(topic)
#     else:
#         authorization = request.headers.get("Authorization")
#         if not authorization:
#             return Response(status_code=401, content=f"Not Authenticated")
#         scheme, _, param = authorization.partition(" ") # param contains token val
#         if (scheme.lower() != "bearer"):
#             return Response(status_code=401, content=f"Not Authenticated")
#         current_user = get_current_user(param)
#         if categories_services.has_access_to_private_category(current_user.user_id, category.category_id):
#             return topics_services.topic_with_replies(topic)
#         else:
#             return Response(status_code=403, content=f"Access denied")


@topics_router.post('/')
def create_topic(new_topic: TopicCreate, current_user: UserAuthDep):
    category = topics_services.get_category_by_name(new_topic.category_name)
    if not category:
        return Response(status_code=404, content=f"Category with name: {new_topic.category_name} does not exist")

    if category.is_locked:
        return Response(status_code=403,
                        content=f"Category #ID:{category.category_id}, name: {category.name} is locked")

    if not category.is_private:
        result = topics_services.create(new_topic, current_user)
    else:
        if categories_services.has_write_access(current_user.user_id, category.category_id):
            result = topics_services.create(new_topic, current_user)
        else:
            return Response(status_code=403, content=f"There is not permission to post in the private category")

    if isinstance(result, int):
        return f'Topic {result} was successfully created!'
    return BadRequest(result)
    # return topics_services.create(new_topic, current_user)


@topics_router.put('/{topic_id}')
def update_topic(topic_id: int, current_user: UserAuthDep, topic_update: TopicUpdate = Body(...)):
    if not topic_update:  # if topic_update.title == None and topic_update.status == None and topic_update.best_reply_id == None:
        return Response(status_code=400, content=f"Data not provided to make changes")

    existing_topic = topics_services.get_by_id(topic_id)
    if not existing_topic:
        return Response(status_code=404, content=f"Topic with id:{topic_id} does not exist!")

    if existing_topic.status == Status.LOCKED:
        return Response(status_code=403, content=f"Topic #ID:{existing_topic.topic_id} is locked")

    category = topics_services.get_category_by_name(existing_topic.category)

    if not category.is_private:
        result = topics_services.topic_updates(topic_id, current_user, topic_update)
        if not result:
            return Response(status_code=400, content="Invalid or insufficient data provided for update")
        else:
            return result

    else:
        if categories_services.has_write_access(current_user.user_id, category.category_id):
            result = topics_services.topic_updates(topic_id, current_user, topic_update)
            if not result:
                return Response(status_code=400, content="Invalid or insufficient data provided for update")
            else:
                return result
        else:
            return Response(status_code=403,
                            content=f"There is not permission to change topics in the private category")
