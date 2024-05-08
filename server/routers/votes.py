from typing import Annotated
from fastapi import APIRouter, HTTPException
from pydantic import StringConstraints
from common.oauth import UserAuthDep
from common.responses import SC
from services import votes_services
from services.replies_services import exists as reply_exists, can_user_access_topic_content
from services.topics_services import exists as topic_exists


votes_router = APIRouter(
    prefix='/topics/{topic_id}/replies/{reply_id}/votes', tags=['votes'])

allowed_vote_type = Annotated[str, StringConstraints(pattern=r'^(up|down)$')]


@votes_router.get('/')
def get_all_votes_for_reply_by_type(reply_id: int, topic_id: int, type: allowed_vote_type, current_user: UserAuthDep):
    """
    Returns all votes for a reply by type (up|down)
    """

    if not topic_exists(id=topic_id):
        raise HTTPException(
            status_code=SC.NotFound,
            detail='No such topic'
        )

    if not reply_exists(reply_id=reply_id, topic_id=topic_id):
        raise HTTPException(
            status_code=SC.NotFound,
            detail='No such reply in this topic'
        )

    user_modify_vote, msg = can_user_access_topic_content(
        topic_id=topic_id, user_id=current_user.user_id)

    if not user_modify_vote:
        raise HTTPException(
            status_code=SC.Forbidden,
            detail=msg
        )

    result = votes_services.get_all(reply_id=reply_id, type=type)
    return {f'Total {type}votes': result}


@votes_router.put('/', status_code=SC.Created)
def add_or_switch(type: allowed_vote_type,
                  reply_id: int, topic_id: int, current_user: UserAuthDep):
    """
    1. Creates a vote of the specified type (up|down), if:
        - topic exists
        - reply exists in this topic
        - user can modify content in this topic
    2. If the user has already up/down voted this reply, switches it, if different
    3. If the vote type given is the same as before, displays a message
    """

    if not topic_exists(id=topic_id):
        raise HTTPException(
            status_code=SC.NotFound,
            detail='No such topic'
        )

    if not reply_exists(reply_id=reply_id, topic_id=topic_id):
        raise HTTPException(
            status_code=SC.NotFound,
            detail='No such reply in this topic'
        )

    user_modify_vote, msg = can_user_access_topic_content(
        topic_id=topic_id, user_id=current_user.user_id)

    if not user_modify_vote:
        raise HTTPException(
            status_code=SC.Forbidden,
            detail=msg
        )

    vote = votes_services.get_vote_with_type(
        reply_id=reply_id, user_id=current_user.user_id)

    if not vote:
        votes_services.add_vote(
            user_id=current_user.user_id, reply_id=reply_id, type=type)
        return f'You {type}voted REPLY with ID: {reply_id}'

    if vote != type:
        votes_services.switch_vote(user_id=current_user.user_id,
                                   reply_id=reply_id, type=vote)
        return f'Vote switched to {type}vote'

    return f'Reply already {type}voted. Choose different type to switch it'


@votes_router.delete('/', status_code=SC.NoContent)
def remove_vote(topic_id: int, reply_id: int, current_user: UserAuthDep):
    """
    1. Removes user's vote, if:
        - topic exists
        - reply exists in this topic
        - user can modify content in this topic
    2. Does nothing, if no such vote
    """
    if not topic_exists(id=topic_id):
        raise HTTPException(
            status_code=SC.NotFound,
            detail='No such topic'
        )

    if not reply_exists(reply_id=reply_id, topic_id=topic_id):
        raise HTTPException(
            status_code=SC.NotFound,
            detail='No such reply in this topic'
        )

    user_modify_vote, msg = can_user_access_topic_content(
        topic_id=topic_id, user_id=current_user.user_id)

    if not user_modify_vote:
        raise HTTPException(
            status_code=SC.Forbidden,
            detail=msg
        )

    votes_services.delete_vote(reply_id=reply_id, user_id=current_user.user_id)
