from fastapi import APIRouter, Depends
from data.models import Topic, User
from services import topics_services
from pydantic import BaseModel
from common.auth import get_user_or_raise_401

class TopicWithRepliesResponseModel(BaseModel):
    pass

topics_router = APIRouter(prefix='/topics')

@topics_router.get('/')
def get_topics():
    pass
    #topics = topics_services.get_all()
    #return topics


@topics_router.get('/{id}')
def get_topic_by_id(id: int):
    pass
    #topic = topics_services.get_by_id(id)
    #return TopicWithRepliesResponseModel()


@topics_router.post('/')
def create_topic(topic: Topic, current_user: User = Depends(get_user_or_raise_401)):
    pass
    

@topics_router.put('/{id}')
def update_topic(id: int, topic: Topic):
    pass

