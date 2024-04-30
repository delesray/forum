from typing import Annotated
from fastapi import APIRouter, Response, Body, HTTPException, Header
from services import topics_services, categories_services
from common.responses import BadRequest, NotFound, Forbidden, Unauthorized
from common.oauth import UserAuthDep
from data.models import TopicUpdate, TopicCreate, Status
#from starlette.requests import Request
from common.oauth import get_current_user


topics_router = APIRouter(prefix='/topics', tags=['topics'])


#TODO pagination for the get_all_topics endpoint to be implemented

@topics_router.get('/')
def get_all_topics(
        x_token: Annotated[str | None, Header()] = None,
        sort: str | None = None,
        sort_by: str = 'topic_id',
        search: str | None = None,
        username: str | None = None,
        category: str | None = None,
        status: str | None = None
    ):
        
        topics = topics_services.get_all(search=search, username=username, category=category, status=status)
        
        if x_token:
            user = get_current_user(x_token)
            private_topics = topics_services.get_topics_from_private_categories(user) 
            topics.extend(private_topics)   
       
        if sort and (sort == 'asc' or sort == 'desc'):
            return topics_services.custom_sort(topics, attribute=sort_by, reverse=sort == 'desc')
        else:
            return topics
    


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int, x_token: Annotated[str | None, Header()] = None):
    topic = topics_services.get_by_id(topic_id)
    if not topic:
        return NotFound(f"Topic #ID:{topic_id} does not exist")
    
    category = categories_services.get_by_id(topic.category_id)

    if not category.is_private:
        return topics_services.topic_with_replies(topic)
    
    else:
        if not x_token:
              return Unauthorized(f"You are not authenticated. Please provide a valid authentication token to access this resource.")
          
        user = get_current_user(x_token)
        
        if not categories_services.has_access_to_private_category(user.user_id, category.category_id):
            return Forbidden(f'You do not have permission to access this private category')
        
        return topics_services.topic_with_replies(topic)

   


@topics_router.post('/')
def create_topic(new_topic: TopicCreate, current_user: UserAuthDep):
    category = categories_services.get_by_id(new_topic.category_id)
    
    if not category: #Do we need such level of detail or more general "No such category" is enough?
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



@topics_router.put('/{topic_id}')
def update_topic(topic_id: int, current_user: UserAuthDep, topic_update: TopicUpdate = Body(...)):
    if not topic_update:  # if topic_update.title == None and topic_update.status == None and topic_update.best_reply_id == None:
        return BadRequest(f"Data not provided to make changes")

    existing_topic = topics_services.get_by_id(topic_id)
    if not existing_topic:
        return NotFound(f"Topic #ID:{topic_id} does not exist")

    if existing_topic.status == Status.LOCKED:
        return Forbidden(f"Topic #ID:{existing_topic.topic_id} is locked")
    
    if existing_topic.user_id != current_user.user_id:
        return Forbidden('You are not allowed to edit topics created by other users')
         
    result = topics_services.topic_updates(topic_id, current_user, topic_update)
    if not result:
        return BadRequest("Invalid or insufficient data provided for update")
    
    return result

