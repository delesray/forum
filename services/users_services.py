from data.models import User
from data.database import read_query, update_query, insert_query


def get_all():
    data = read_query(
        '''SELECT user_id, username, email, first_name, last_name, is_admin
        FROM users''')

    users = [User.from_query(*row) for row in data]
    return users


def get_by_id(id):
    data = read_query(
        '''SELECT user_id, username, email, first_name, last_name, is_admin
        FROM users WHERE user_id = ?''', (id,))

    user = [User.from_query(*row) for row in data][0]
    return user
