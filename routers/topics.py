from fastapi import APIRouter, Response, Body, HTTPException
from services import topics_services, replies_services, categories_services
from common.responses import BadRequest
from common.auth import UserAuthDep
from data.models import  TopicUpdate, TopicCreate, Status



topics_router = APIRouter(prefix='/topics', tags=['topics'])


# pagination for the get_all_topics endpoint to be implemented
# logic for the cases when the user has access to the private categories to be implemented
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
        return Response(status_code=404, content=f"Topic with id:{topic_id} does not exist")
    
    category_id = topics_services.get_category_id(topic.category) 
    category = categories_services.get_by_id(category_id)
    
    if not category.is_private:
        return topics_services.topic_with_replies(topic)
    else:
        current_user = UserAuthDep()
        if categories_services.has_access_to_private_category(current_user.user_id, category.category_id):
            return topics_services.topic_with_replies(topic)
        else:
            return Response(status_code=403, content=f"Access denied")


@topics_router.post('/')                                   
def create_topic(new_topic: TopicCreate, current_user: UserAuthDep):
        
    if new_topic.category_name not in topics_services.get_categories_names():
            return Response(status_code=404, content=f"Category with name: {new_topic.category_name} does not exist")
    
    result = topics_services.create(new_topic, current_user)
    if isinstance(result, int):
        return f'Topic {result} was successfully created!'
    return BadRequest(result)
    #return topics_services.create(new_topic, current_user)
    


@topics_router.put('/{topic_id}') 
def update_topic(topic_id: int, current_user: UserAuthDep, topic_update: TopicUpdate = Body(...)):
    if not topic_update:  # if topic_update.title == None and topic_update.status == None and topic_update.best_reply_id == None:
        return Response(status_code=400, content=f"Data not provided to make changes")

    existing_topic = topics_services.get_by_id(topic_id)
    if not existing_topic:
        return Response(status_code=404, content=f"Topic with id:{topic_id} does not exist!")

    if topic_update.title and len(topic_update.title) >= 1:
        return topics_services.update_title(topic_id, topic_update.title)

    if topic_update.status and current_user.is_admin and topic_update.status in [Status.OPEN, Status.LOCKED]:
        return topics_services.update_status(topic_id, topic_update.status)

    if topic_update.best_reply_id:
        topic_replies_ids = topics_services.get_topic_replies(topic_id)
        if not topic_replies_ids:
            return Response(status_code=404, content=f"Topic with id:{topic_id} does not have replies")

        if topic_update.best_reply_id in topic_replies_ids:
            return topics_services.update_best_reply(topic_id, topic_update.best_reply_id)

    return Response(status_code=400, content="Invalid or insufficient data provided for update")
