from fastapi import APIRouter, HTTPException
from data.models import MessageCreate
from services import messages_services, users_services
from common.oauth import UserAuthDep


messages_router = APIRouter(prefix='/messages', tags=['messages'])
#
# @messages_router.get("/conversations/{other_user_id}/", response_model=list[Message])
# def view_conversation(other_user_id: int, current: User = Depends(get_user_or_raise_401)):
#     pass
#     # messages = get_messages_between_users(current.user_id, user_id)
#
#
# @messages_router.get("/conversations/", response_model=list[User])
# def view_conversations(current: User = Depends(get_user_or_raise_401)):
#     pass
#     # conversations = get_conversations_for_user(current.user_id)
#
#
# @messages_router.post("/messages/")
# def create_message(message: Message, current: User = Depends(get_user_or_raise_401)):
#     receiver = users_services.get_by_id(message.receiver_id)
#     if receiver is None:
#         return Response(status_code=404, content="Recipient not found")
#
#     new_message = messages_services.create_new_message(message.text, current.user_id, receiver.user_id)
#
#     return new_message
#
#
# @messages_router.put("/messages/{message_id}")
# def update_message(message_id: int, message_update: Message, current: User = Depends(get_user_or_raise_401)):
#     pass

# todo flag for deleting messege

@messages_router.post('/')
def create_message(new_message: MessageCreate, current_user: UserAuthDep):
    if not new_message.text:
        raise HTTPException(status_code=400, detail="Message text is required")
    
    if not new_message.receiver_id:
        raise HTTPException(status_code=400, detail="Receiver ID is required")
    
    receiver = users_services.get_by_id(new_message.receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    result = messages_services.create(new_message.text, current_user.user_id, new_message.receiver_id)
    
    if isinstance(result, int):
        return f'Message ID: {result} was successfully created!'
    else:
        raise HTTPException(status_code=400)

   
    
     