from fastapi import APIRouter, Response, Body
from data.models import Topic, TopicUpdate
from services import topics_services, replies_services
from common.responses import BadRequest
from common.auth import get_user_or_raise_401

topics_router = APIRouter(prefix='/topics', tags=['topics'])
topics_router = APIRouter(prefix='/topics')


# pagination for the get_all_topics endpoint to be implemented
@topics_router.get('/')
def get_all_topics(
        sort: str | None = None,
        sort_by: str = 'topic_id',
        search: str | None = None,
        username: str | None = None,
        category: str | None = None,
        status: str | None = None
):
    topics = topics_services.get_all(search=search, username=username, category=category, status=status)
    if not topics:
        return []
    if sort and (sort == 'asc' or sort == 'desc'):
        return topics_services.custom_sort(topics, attribute=sort_by, reverse=sort == 'desc')
    else:
        return topics


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int):
    topic = topics_services.get_by_id(topic_id)
    if not topic:
        return Response(status_code=404, content=f"Topic with id:{topic_id} does\'t exist!")
    replies = replies_services.get_all(topic_id)

    topic_with_replies = {
        "topic": topic,
        "replies": replies if replies else []
    }

    return topic_with_replies


@topics_router.post('/')
def create_topic(topic: Topic):  # def create_topic(topic: Topic, current_user: User = Depends(get_user_or_raise_401)):
    result = topics_services.create(topic)
    if isinstance(result, int):
        return f'Topic {result} was successfully created!'
    return BadRequest(result)


@topics_router.put('/{topic_id}')
def update_topic(topic_id: int, topic_update: TopicUpdate = Body(...)):
    if not topic_update:  # if topic_update.title == None and topic_update.status == None and topic_update.best_reply_id == None:
        return Response(status_code=400, content=f"Data not provided to make changes")

    existing_topic = topics_services.get_by_id(topic_id)
    if not existing_topic:
        return Response(status_code=404, content=f"Topic with id:{topic_id} does not exist!")

    if topic_update.title and len(topic_update.title) >= 1:
        return topics_services.update_title(topic_id, topic_update.title)

    if topic_update.status and topic_update.status in ["open", "locked"]:
        return topics_services.update_status(topic_id, topic_update.status)

    if topic_update.best_reply_id:
        topic_replies_ids = topics_services.get_topic_replies(topic_id)
        if not topic_replies_ids:
            return Response(status_code=404, content=f"Topic with id:{topic_id} does not have replies")

        if topic_update.best_reply_id in topic_replies_ids:
            return topics_services.update_best_reply(topic_id, topic_update.best_reply_id)

    return Response(status_code=400, content="Invalid or insufficient data provided for update")
