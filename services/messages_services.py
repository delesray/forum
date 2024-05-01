from data.models import Message
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError

# def get_messages_between_users(current.user_id, user_id):
#     pass

# def get_conversations_for_user(current.user_id):
#     pass

# def get_message_by_id(message_id):
#     pass

# def update(old: Message, new: Message):
#     pass


def create(message_text, sender_id, receiver_id):

    try:
        generated_id = insert_query(
            'INSERT INTO messages(text, sender_id, receiver_id) VALUES(?,?,?)',
            (message_text, sender_id, receiver_id))

        return generated_id
        
    except IntegrityError as e:
        return e
