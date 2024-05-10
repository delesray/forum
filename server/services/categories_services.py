from data.models.category import Category
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError
from data.models.topic import TopicResponse


def exists_by_name(name) -> bool:
    return any(read_query(
        '''SELECT 1 FROM categories WHERE name = ?''', (name,)))


def get_all(search: str | None = None) -> list[Category]:
    sql = '''SELECT category_id, name, is_locked, is_private
        FROM categories'''

    query_params = ()

    if search:
        sql += ' WHERE name LIKE ?'
        query_params += (f'%{search}%',)

    result = read_query(sql, query_params)
    categories = [Category.from_query(*row) for row in result]

    return categories


def get_by_id(category_id) -> Category | None:
    data = read_query(
        '''SELECT category_id, name, is_locked, is_private
        FROM categories WHERE category_id = ?''', (category_id,))
    if data:
        return Category.from_query(*data[0])


def create(category: Category) -> Category | IntegrityError:
    """
    Handles unique columns violations with try/except
    """
    try:
        generated_id = insert_query(
            'INSERT INTO categories(name) VALUES(?)',
            (category.name,)
        )
        category.category_id = generated_id
        return category
    except IntegrityError as e:
        return e


def has_access_to_private_category(user_id: int, category_id: int) -> bool:
    return any(read_query(
        '''SELECT 1
           FROM users_categories_permissions
           WHERE user_id = ? AND category_id = ?''',
        (user_id, category_id,)))


def update_privacy(privacy: bool, category_id: int) -> None:
    update_query('UPDATE categories SET is_private = ? WHERE category_id = ?',
                 (privacy, category_id,))


def update_locking(locking: bool, category_id: int) -> None:
    update_query('UPDATE categories SET is_locked = ? WHERE category_id = ?',
                 (locking, category_id,))


def get_user_access_level(user_id: int, category_id: int) -> bool | None:
    data = read_query(
        '''SELECT write_access FROM users_categories_permissions 
        WHERE user_id = ? AND category_id = ?''', (user_id, category_id,)
    )
    if data:
        return data[0][0]


def update_user_access_level(user_id: int, category_id: int, access: bool) -> None:
    update_query(
        '''UPDATE users_categories_permissions SET write_access = ?
        WHERE user_id = ? AND category_id = ?''', (access, user_id, category_id)
    )


def is_user_in(user_id: int, category_id: int) -> bool:
    data = read_query(
        '''SELECT 1 FROM users_categories_permissions 
        WHERE user_id = ? AND category_id = ?''', (user_id, category_id,)
    )
    return any(data)


def add_user(user_id: int, category_id: int) -> None:
    insert_query('INSERT INTO users_categories_permissions(user_id,category_id) VALUES(?,?)',
                 (user_id, category_id,))


def remove_user(user_id: int, category_id: int) -> None:
    update_query('DELETE FROM users_categories_permissions WHERE user_id = ? AND category_id = ?',
                 (user_id, category_id,))


def has_write_access(user_id: int, category_id: int) -> bool:
    return any(read_query(
        '''SELECT 1
           FROM users_categories_permissions
           WHERE user_id = ? AND category_id = ? AND write_access = ?''',
        (user_id, category_id, 1))
    )


def get_privileged_users(category_id) -> list:
    data = read_query(
        '''SELECT ucp.user_id, u.username, ucp.write_access
        FROM users_categories_permissions as ucp JOIN users as u
        WHERE ucp.category_id = ?''', (category_id,)
    )
    if data:
        return data


def response_obj_privileged_users(category: Category, users: list[tuple]) -> dict:
    """
    Shows the bigger access users first
    """
    users = list(sorted(users, key=lambda x: -x[-1]))
    users_dict = {}
    for uid, username, access in users:
        users_dict[uid] = f'{username}: {'write' if access else 'read'} access'

    return {
        'category': category.name,
        'users': users_dict
    }


def get_topics_by_cat_id(category_id: int) -> list[TopicResponse] | None:
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
               FROM topics t 
               JOIN users u ON t.user_id = u.user_id
               JOIN categories c ON t.category_id = c.category_id WHERE t.category_id = ?''', (category_id,))

    return [TopicResponse.from_query(*row) for row in data] if data else None
