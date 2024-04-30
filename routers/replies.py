from fastapi import APIRouter
from common.responses import Forbidden, NotFound
from data.models import Reply
from services import replies_services
from common.oauth import UserAuthDep
from services.replies_services import get_by_id as get_reply_by_id, can_user_modify_reply


replies_router = APIRouter(prefix='/topics/{topic_id}/replies', tags=['replies'])

# get all votes per reply

@replies_router.post('/', status_code=201)
def add_reply(topic_id: int, reply: Reply, user: UserAuthDep):

    user_modify_reply, msg = can_user_modify_reply(topic_id=topic_id, user_id=user.user_id)

    if not user_modify_reply:
        return Forbidden(msg)

    result = replies_services.create_reply(topic_id, reply, user.user_id)
    return result


@replies_router.put('/{reply_id}', status_code=204)
def edit_reply(topic_id: int, reply_id: int, update: Reply, user: UserAuthDep):

    reply_to_update = get_reply_by_id(reply_id)

    if not reply_to_update:
        return NotFound()
    
    user_modify_reply, msg = can_user_modify_reply(topic_id=topic_id, user_id=user.user_id)
    
    if not user_modify_reply:
        return Forbidden(msg)
    
    if reply_to_update.user_id != user.user_id:
        return Forbidden('You cannot edit another user\'s reply')

    replies_services.update_reply(reply_id, update.text)


@replies_router.delete('/{reply_id}', status_code=204)
def delete_reply(topic_id: int, reply_id: int, user: UserAuthDep):
    
    reply_to_delete = get_reply_by_id(reply_id)

    if not reply_to_delete:
        return NotFound()
    
    user_modify_reply, msg = can_user_modify_reply(topic_id=topic_id, user_id=user.user_id)
    
    if not user_modify_reply:
        return Forbidden(msg)
    
    if reply_to_delete.user_id != user.user_id:
        return Forbidden('You cannot delete another user\'s reply')
    
    # delete from table?
    replies_services.delete_reply(reply_id)
