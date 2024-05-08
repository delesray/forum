from data.models.user import User, UserRegister, UserUpdate, UserInfo
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from common.utils import hash_pass, verify_password


def get_all() -> list[UserInfo]:
    data = read_query(
        '''SELECT username, email, first_name, last_name
        FROM users WHERE NOT is_deleted = ?''', (1,))

    users = [UserInfo.from_query(*row) for row in data]
    return users


def exists_by_username(username) -> bool:
    return any(read_query(
        '''SELECT 1 FROM users WHERE username = ? AND NOT is_deleted = ?''', (username, 1)))


def get_by_id(user_id) -> UserInfo:
    data = read_query(
        '''SELECT username, email, first_name, last_name
        FROM users WHERE user_id = ? AND NOT is_deleted = ?''', (user_id, 1))

    if data:
        return UserInfo.from_query(*data[0])


def find_by_username(username: str) -> User | None:
    data = read_query(
        '''SELECT user_id, username, password, email, first_name, last_name, is_admin FROM users 
        WHERE username = ? AND NOT is_deleted = ?''',
        (username, 1))

    return next((User.from_query(*row) for row in data), None)


def register(user: UserRegister) -> User | IntegrityError:
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
            (user.username, hashed_password, user.email,
             user.first_name, user.last_name)
        )
        return generated_id
    except IntegrityError as e:
        return e


def try_login(username: str, password: str) -> User | None:
    user = find_by_username(username)

    if user and verify_password(password, user.password):
        return user


def update(old: User, new: UserUpdate) -> UserUpdate:
    """
    Merges new user with old
    Handles columns violations with try/except
    """

    merged = UserUpdate(
        first_name=new.first_name or old.first_name,
        last_name=new.last_name or old.last_name
    )

    update_query(
        'UPDATE users SET first_name = ?, last_name = ? WHERE user_id = ?',
        (merged.first_name, merged.last_name, old.user_id)
    )

    return merged


def change_password(user_id: int, new_hashed_password: str) -> None:
    update_query('UPDATE users SET password = ? WHERE user_id = ?',
                 (new_hashed_password, user_id))


def delete(user_id: int) -> None:
    update_query(
        'UPDATE users SET is_deleted = ? WHERE user_id = ?;', (True, user_id)
    )
