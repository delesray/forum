from fastapi import APIRouter
from common.responses import Forbidden, NotFound
from data.models import Reply
from services import replies_services
from common.auth import UserAuthDep
from services.topics_services import get_by_id as get_topic_by_id
from services.replies_services import get_by_id as get_reply_by_id


replies_router = APIRouter(prefix='/topics/{topic_id}/replies', tags=['replies'])


@replies_router.post('/')
def add_reply(topic_id: int, reply: Reply, user: UserAuthDep):

    topic = get_topic_by_id(topic_id)

    if topic.status == 'locked':
        return Forbidden('This topic is read-only')

    result = replies_services.create_reply(topic_id, reply, user.user_id)
    return result


@replies_router.put('/{reply_id}', status_code=204)
def edit_reply(reply_id: int, update: Reply, user: UserAuthDep):
    reply_to_update = get_reply_by_id(reply_id)

    if not reply_to_update:
        return NotFound('No such reply for this topic')
    elif reply_to_update.user_id != user.user_id:
        return Forbidden('You cannot edit another user\'s reply')

    replies_services.update_reply(reply_id, update.text)


@replies_router.delete('/{reply_id}')
def delete_reply(reply_id: int):
    # delete or flag deleted?
    pass

