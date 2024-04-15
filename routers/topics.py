from fastapi import APIRouter, Depends, Response
from data.models import Topic, User
from services import topics_services, replies_services
from pydantic import BaseModel
from common.auth import get_user_or_raise_401



topics_router = APIRouter(prefix='/topics')

#pagination for the get_all_topics endpoint to be implemented 
@topics_router.get('/')
def get_all_topics(
    sort: str = None or None,
    sort_by: str = None or None,
    search: str = None or None
    ):

    topics = topics_services.get_all(search)
    if sort and (sort == 'asc' or sort == 'desc') and sort_by:
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
def create_topic(topic: Topic):  #def create_topic(topic: Topic, current_user: User = Depends(get_user_or_raise_401)):
    result, code = topics_services.create(topic)
    return Response(status_code=code, content=result)

    

@topics_router.put('/{topic_id}', status_code=200)
def update_topic(topic_id: int, topic: Topic):
    existing_topic = topics_services.get_by_id(topic_id)
    if not existing_topic:
        return Response(status_code=404, content=f"Topic with id:{topic_id} does\'t exist!")

    result, code = topics_services.update(existing_topic, topic)
    return result

