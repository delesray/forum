from fastapi import APIRouter, Response
from data.models import Reply
from services import replies_services


replies_router = APIRouter(prefix='/topics')

# This exists in topics router
# @replies_router.get('/{topic_id}')
# def get_all_replies_per_topic(topic_id: int):
#     replies = replies_services.get_all(topic_id)

#     if not replies:
#         return Response(status_code=204)
    
#     return replies


# TODO
# this can be moved to topics router and create_reply - to update_topic in topics_services
@replies_router.post('/{topic_id}')
def add_reply(topic_id: int, reply: Reply):
    result = replies_services.create_reply(topic_id, reply)

    return result


# TODO 
# can a user change their reply?
