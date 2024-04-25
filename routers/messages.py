from fastapi import APIRouter, Depends, Response
from data.models import Message, User
from services import messages_services, users_services
from common.auth import UserAuthDep

messages_router = APIRouter


@messages_router.get("/conversations/{other_user_id}/", response_model=list[Message])
def view_conversation(other_user_id: int, current_user: UserAuthDep):
    pass
    # messages = get_messages_between_users(current.user_id, user_id)


@messages_router.get("/conversations/", response_model=list[User])
def view_conversations(current_user: UserAuthDep):
    pass
    # conversations = get_conversations_for_user(current.user_id)


@messages_router.post("/messages/")
def create_message(message: Message, current_user: UserAuthDep):
    receiver = users_services.get_by_id(message.receiver_id)
    if receiver is None:
        return Response(status_code=404, content="Recipient not found")

    new_message = messages_services.create_new_message(message.text, current.user_id, receiver.user_id)

    return new_message


@messages_router.put("/messages/{message_id}")
def update_message(message_id: int, message_update: Message, current_user: UserAuthDep):
    pass

# todo flag for deleting messege
