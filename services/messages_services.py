from data.models import Message
from data.database import read_query, update_query, insert_query

def get_messages_between_users(current.user_id, user_id):
    pass

def get_conversations_for_user(current.user_id):
    pass

def get_message_by_id(message_id):
    pass

def update(old: Message, new: Message):
    pass

def create_new_message(message.text, current.user_id, recipient.user_id):
    pass