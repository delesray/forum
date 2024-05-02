from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, Header, Request
from services import topics_services, categories_services
from common.oauth import UserAuthDep
from common.responses import BadRequest, NotFound, Forbidden
from data.models import TopicUpdate, TopicCreate, TopicResponse
from common.oauth import get_current_user
from fastapi_pagination import paginate
from fastapi_pagination.links import Page


topics_router = APIRouter(prefix='/topics', tags=['topics'])


@topics_router.get('/')
def get_all_topics(
    sort: str | None = None,
    sort_by: str = 'topic_id',
    search: str | None = None,
    username: str | None = None,
    category: str | None = None,
    status: str | None = None
) -> Page[TopicResponse]:
                
    topics = topics_services.get_all(search=search, username=username, category=category, status=status)  
        
    #TODO pagination should work on db level for optimal result
    if sort and (sort == 'asc' or sort == 'desc'):
        return paginate(topics_services.custom_sort(topics, attribute=sort_by, reverse=sort == 'desc'))
    else:
        return paginate(topics)


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int, req: Request):
    topic = topics_services.get_by_id(topic_id)

    if not topic:
        raise HTTPException(
            status_code=404,
            detail=f"Topic #ID:{topic_id} does not exist"
        )
    
    category = categories_services.get_by_id(topic.category_id)

    if not category.is_private:
        return topics_services.topic_with_replies(topic)
    
    authorization = req.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail='Login to view topics in private categories'
        )
    
    _, _, token = authorization.partition(" ") 
          
    #token = req.headers.get('Authorization').split()[1]
    
    # if not token:
    #     raise HTTPException(
    #         status_code=401,
    #         detail='Login to view topics in private categories'
    #     )
    
    existing_user = get_current_user(token)

    if not categories_services.has_access_to_private_category(existing_user.user_id, category.category_id):
        raise HTTPException(
            status_code=403,
            detail=f'You do not have permission to access this private category'
        )
        
    return topics_services.topic_with_replies(topic)


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

#separate models TitleUpdate and BestReplyUpdate instaed of the single TopicUpdate model?   
        
@topics_router.patch('/{topic_id}/title')
def update_topic_title(topic_id: int, current_user: UserAuthDep, topic_update: TopicUpdate = Body(...)):
    if not topic_update.title:  
        return BadRequest(f"Data not provided to make changes")
    
    error_response = topics_services.validate_topic_access(topic_id, current_user)
    if error_response:
        return error_response
    
    return topics_services.update_title(topic_id, topic_update.title)
    

    
    

