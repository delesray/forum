from http.client import HTTPException
from fastapi import APIRouter
from common.oauth import UserAuthDep
from services import votes_services
from services.replies_services import exists as reply_exists
from services.topics_services import exists as topic_exists

votes_router = APIRouter(prefix='/topics/{topic_id}/replies/{reply_id}/votes', tags=['votes'])


@votes_router.get('/', status_code=200)
def get_all_votes_for_reply(reply_id: int, topic_id: int, type: str, user: UserAuthDep):
    if not topic_exists(id=topic_id):
        raise HTTPException(
            status_code=404,
            detail='No such topic'
        )

    if not reply_exists(id=reply_id):
        raise HTTPException(
            status_code=404,
            detail='No such reply'
        )

    result = votes_services.get_all(reply_id=reply_id, type=type)
    return result


@votes_router.put('/', status_code=201)
def add_or_switch(type: str, reply_id, topic_id, user: UserAuthDep):
    if not topic_exists(id=topic_id):
        raise HTTPException(
            status_code=404,
            detail='No such topic'
        )

    if not reply_exists(id=reply_id):
        raise HTTPException(
            status_code=404,
            detail='No such reply'
        )

    vote = votes_services.find_vote(reply_id=reply_id, user_id=user.user_id)

    if not vote:
        votes_services.add_vote(user_id=user.user_id, reply_id=reply_id, type=type)
        return f'You {type}voted reply with ID: {reply_id}'

    votes_services.switch_vote(user_id=user.user_id,
                               reply_id=reply_id, type=type)
    return f'Vote switched to {type}vote'


@votes_router.delete('/', status_code=204)
def remove_vote(reply_id: int, user: UserAuthDep):
    votes_services.delete_vote(reply_id=reply_id, user_id=user.user_id)
