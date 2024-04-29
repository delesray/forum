from data.models import User, UserUpdate
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from common.utils import hash_pass, verify_password


def get_all():
    data = read_query(
        '''SELECT user_id, username, password, email, first_name, last_name, is_admin
        FROM users''')

    users = [User.from_query(*row) for row in data]
    return users


def get_by_id(user_id):
    data = read_query(
        '''SELECT user_id, username, password, email, first_name, last_name, is_admin
        FROM users WHERE user_id = ?''', (user_id,))

    user = [User.from_query(*row) for row in data]
    if not user:
        return None

    return user[0]


def find_by_username(username: str) -> User | None:
    data = read_query(
        'SELECT user_id, username, password, email, first_name, last_name, is_admin FROM users WHERE username = ?',
        (username,))

    return next((User.from_query(*row) for row in data), None)


def register(user: User) -> User | IntegrityError:
    """
    Creates user without is_admin
    Handles columns violations with try/except
    todo check what happens if mariadb returns another error type
    """

    # hashing the password and adding it to the db - line 52
    hashed_password = hash_pass(user.password)

    try:
        generated_id = insert_query(
            'INSERT INTO users(username, password, email, first_name, last_name) VALUES(?,?,?,?,?)',
            (user.username, hashed_password, user.email, user.first_name, user.last_name)
        )
        return generated_id
    except IntegrityError as e:
        return e


def try_login(username: str, password: str) -> User | None:
    user = find_by_username(username)

    if user:
        is_pass_verified = verify_password(password, user.password)

    return user if user and is_pass_verified else None


def update(old: User, new: UserUpdate):
    """
    Merges new user with old
    Handles columns violations with try/except
    """

    merged = UserUpdate(
        username=old.username,  # cannot update username
        first_name=new.first_name or old.first_name,
        last_name=new.last_name or old.last_name
    )

    update_query(
        'UPDATE users SET first_name = ?, last_name = ? WHERE user_id = ?',
        (merged.first_name, merged.last_name, old.user_id)
    )

    return merged


def delete(user_id: int):
    return update_query('delete from users where user_id = ?', (user_id,))
