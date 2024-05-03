from fastapi import APIRouter, HTTPException
from data.models import ReplyCreateUpdate
from services import replies_services
from services.topics_services import exists
from common.oauth import UserAuthDep
from services.replies_services import get_by_id as get_reply_by_id, can_user_modify_reply


replies_router = APIRouter(prefix='/topics/{topic_id}/replies', tags=['replies'])


@replies_router.post('/', status_code=201)
def add_reply(topic_id: int, reply: ReplyCreateUpdate, user: UserAuthDep):

    if not exists(id=topic_id):
        raise HTTPException(
            status_code=404,
            detail='No such topic'
        )

    user_modify_reply, msg = can_user_modify_reply(topic_id=topic_id, user_id=user.user_id)

    if not user_modify_reply:
        raise HTTPException(
            status_code=403,
            detail=msg
        )

    reply_id = replies_services.create_reply(topic_id, reply, user.user_id)
    return f'Reply with ID {reply_id} successfully added'


@replies_router.put('/{reply_id}', status_code=204)
def edit_reply(topic_id: int, reply_id: int, update: ReplyCreateUpdate, user: UserAuthDep):

    if not exists(id=topic_id):
        raise HTTPException(
            status_code=404,
            detail='No such topic'
        )

    reply_to_update = get_reply_by_id(reply_id)

    if not reply_to_update:
        raise HTTPException(status_code=404)
    
    user_modify_reply, msg = can_user_modify_reply(topic_id=topic_id, user_id=user.user_id)
    
    if not user_modify_reply:
        raise HTTPException(
            status_code=403,
            detail=msg
        )

    replies_services.update_reply(reply_id, update.text)


@replies_router.delete('/{reply_id}', status_code=204)
def delete_reply(topic_id: int, reply_id: int, user: UserAuthDep):
    
    if not exists(id=topic_id):
        raise HTTPException(
            status_code=404,
            detail='No such topic'
        )

    reply_to_delete = get_reply_by_id(reply_id)

    if not reply_to_delete:
        raise HTTPException(status_code=404)
    
    user_modify_reply, msg = can_user_modify_reply(topic_id=topic_id, user_id=user.user_id)
    
    if not user_modify_reply:
        raise HTTPException(
            status_code=403,
            detail=msg
        )
    
    replies_services.delete_reply(reply_id)
