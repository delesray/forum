from fastapi import APIRouter
from common.oauth import UserAuthDep
from services import votes_services


votes_router = APIRouter(prefix='/topics/{topic_id}/replies/{reply_id}/votes', tags=['votes'])

#TODO check if reply and topic exist?

@votes_router.get('/', status_code=200)
def get_all_votes_for_reply(reply_id: int, type: str, user: UserAuthDep):
    result = votes_services.get_all(reply_id=reply_id, type=type)
    return result


@votes_router.put('/', status_code=201)
def add_or_switch_(type: str, reply_id, user: UserAuthDep):
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
