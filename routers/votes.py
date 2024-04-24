from fastapi import APIRouter
from data.models import Vote
from common.auth import UserAuthDep2


# too long?
votes_router = APIRouter(prefix='/topics/{topic_id}/replies/{reply_id}/votes', tags=['votes'])


@votes_router.get('/')
def get_all_voter_for_reply(reply_id: int):
    pass


@votes_router.post('/')
def add_vote():
    pass


@votes_router.put('/{vote_id}')
def change_vote(id: int):
    pass


@votes_router.delete('/{vote_id}')
def remove_vote(id: int):
    pass
