from fastapi import APIRouter, HTTPException
from data.models.message import MessageText
from services import messages_services, users_services
from common.oauth import UserAuthDep

messages_router = APIRouter(prefix='/messages', tags=['messages'])


@messages_router.post('/{receiver_id}', status_code=201)
def send_message(receiver_id: int, message: MessageText, current_user: UserAuthDep):
    if not message.text:
        raise HTTPException(status_code=400, detail="Message text is required")

    # todo db raises error when no such receiver fkconstr
    receiver = users_services.get_by_id(receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    messages_services.create(message.text, current_user.user_id, receiver_id)
    return f'Message sent'


@messages_router.get('/users')
def get_all_conversations(current_user: UserAuthDep):
    result = messages_services.get_all_conversations(current_user.user_id)

    return result or 'No conversations'


@messages_router.get('/{receiver_id}')
def get_conversation(receiver_id: int, current_user: UserAuthDep):
    result = messages_services.get_conversation(current_user.user_id, receiver_id)

    return result or 'No such conversation'


@messages_router.patch('/{message_id}')
def update_message(message_id: int, message: MessageText, current_user: UserAuthDep):
    if messages_services.exists(message_id):
        raise HTTPException(404, 'No such message')
    messages_services.update_text(message_id, message.text)
