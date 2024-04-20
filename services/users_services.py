from data.models import User
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError

_SEPARATOR = ';'


def get_all():
    data = read_query(
        '''SELECT user_id, username, password, email, first_name, last_name, is_admin
        FROM users''')

    users = [User.from_query(*row) for row in data]
    return users


def get_by_id(user_id):
    data = read_query(
        '''SELECT user_id, username, email, first_name, last_name, is_admin
        FROM users WHERE user_id = ?''', (user_id,))

    user = [User.from_query(*row) for row in data]
    if not user:
        return None

    return user[0]


def find_by_username(username: str):
    data = read_query(
        'SELECT user_id, username, password, email, first_name, last_name, is_admin FROM users WHERE username = ?',
        (username,))

    return next((User.from_query(*row) for row in data), None)


def register(user: User):
    """
    Creates user without is_admin
    Handles unique columns violations with try/except in queries
    todo check what happens if mariadb returns another error type
    """
    # if user.email is not 'correct':
    #     return Response(status_code=400, content='')

    try:
        generated_id = insert_query(
            'INSERT INTO users(username,password, email) VALUES(?,?,?)',
            (user.username, user.password, user.email,)
        )
        return generated_id
    except IntegrityError as e:
        return e


def try_login(username: str, password: str):
    user = find_by_username(username)

    # password = _hash_password(password)
    return user if user and user.password == password else None


def update(old: User, new: User):
    """
    Merges new user with old, changing is_admin attribute only if request is from admin
    Handles unique columns violations with try/except in queries
    """
    request_sent_from_admin = True  # no authorization logic yet

    new_admin_status = old.is_admin
    if request_sent_from_admin:
        new_admin_status = new.is_admin if new.is_admin is not None else old.is_admin

    merged = User(
        user_id=old.user_id,
        username=old.username,  # cannot update username
        password=old.password, 
        email=old.email,  # cannot update email
        first_name=new.first_name or old.first_name,
        last_name=new.last_name or old.last_name,
        is_admin=new_admin_status
    )
    update_query(
        'UPDATE users SET first_name = ?, last_name = ?, is_admin = ? WHERE user_id = ?',
        (merged.first_name, merged.last_name, merged.is_admin, merged.user_id)
    )

    return merged


def is_authenticated(token: str) -> bool:
    return any(read_query(
        'SELECT 1 FROM users where user_id = ? and username = ?',
        # note: this token is not particulary secure, use JWT for real-world user
        token.split(_SEPARATOR)[0:2]))


def from_token(token: str) -> User | None:
    _, username, _ = token.split(_SEPARATOR)

    return find_by_username(username)


def create_token(user: User):
    return f'{user.user_id}{_SEPARATOR}{user.username}{_SEPARATOR}{user.is_admin}'


def delete(user_id: int):
    return update_query('delete from users where user_id = ?', (user_id,))