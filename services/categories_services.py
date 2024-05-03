from data.models.category import Category, CategoryWithTopics
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError

from data.models.topic import TopicResponse, Topic


def get_all(search: str | None) -> list[Category]:
    sql = '''SELECT category_id, name, is_locked, is_private
        FROM categories'''

    query_params = ()

    if search:
        sql += ' WHERE name LIKE ?'
        query_params += (f'%{search}%',)

    result = read_query(sql, query_params)
    categories = [Category.from_query(*row) for row in result]

    return categories


def get_by_id(category_id, with_topics=None) -> Category | None | CategoryWithTopics:
    data = read_query(
        '''SELECT category_id, name, is_locked, is_private
        FROM categories WHERE category_id = ?''', (category_id,))
    if not data:
        return None

    if with_topics:
        return CategoryWithTopics.from_query(*data[0])

    return Category.from_query(*data[0])


def dto(data):
    topics = []

    for cid, cname, cislocked, cisprivate, tid, ttile, tuserid, tislocked, tbrid, tcategoryid in data:
        if any(data[0][4:]):  # if topics
            topics.append(
                Topic.from_query(*(tid, ttile, tuserid, tislocked, tbrid, tcategoryid))
            )

    category = CategoryWithTopics.from_query(cid, cname, cislocked, cisprivate, topics)
    return category


def get_cat_by_id_with_topics(category_id, search=None, sort=None) -> None | CategoryWithTopics:
    sql = '''SELECT c.category_id, c.name, c.is_locked, c.is_private,
        t.topic_id, t.title, t.user_id, t.is_locked, t.best_reply_id, t.category_id
        FROM categories as c 
        LEFT JOIN topics as t 
        ON c.category_id = t.category_id
        WHERE c.category_id = ?'''
    
    query_params = (category_id,)

    if search:
        sql += ' AND t.title LIKE ?'
        query_params += (f'%{search}%',)

    # db sort to avoid in-memory sort
    if sort and (sort.lower() in ('asc', 'desc')):
        sql += f' ORDER BY t.title {sort}'

    data = read_query(sql, query_params)
    
    if not data:
        return None

    category_dto = dto(data)
    return category_dto


def create(category):
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


def update(old: Category, new: Category):
    """
    Merges new category with old, changing
    Handles unique columns violations with try/except in queries
    """
    request_sent_from_admin = True  # no authorization logic yet

    new_is_locked, new_is_private = old.is_locked, old.is_private
    if request_sent_from_admin:
        new_is_locked = new.is_locked if new.is_locked is not None else old.is_locked
        new_is_private = new.is_private if new.is_private is not None else old.is_private

    merged = Category(
        category_id=old.category_id,
        name=new.name or old.name,  # only admin changes name
        is_locked=new_is_locked,
        is_private=new_is_private
    )
    data = update_query(
        'UPDATE categories SET name = ?, is_locked = ?, is_private = ? WHERE category_id = ?',
        (merged.name, merged.is_locked, merged.is_private, merged.category_id)
    )

    # todo to finish


def has_access_to_private_category(user_id: int, category_id: int):
    return any(read_query(
        '''SELECT 1
           FROM users_categories_permissions
           WHERE user_id = ? AND category_id = ?''',
        (user_id, category_id)))


def update_privacy(privacy: bool, category_id: int):
    update_query('UPDATE categories SET is_private = ? WHERE category_id = ?',
                 (privacy, category_id))


def update_locking(locking: bool, category_id: int):
    update_query('UPDATE categories SET is_locked = ? WHERE category_id = ?',
                 (locking, category_id))


def get_user_access_level(user_id: int, category_id: int) -> bool | None:
    data = read_query(
        '''SELECT write_access FROM users_categories_permissions 
        WHERE user_id = ? AND category_id = ?''', (user_id, category_id,)
    )
    if data:
        return data[0][0]


def update_user_access_level(user_id: int, category_id: int, access: bool):
    update_query(
        '''UPDATE users_categories_permissions SET write_access = ?
        WHERE user_id = ? AND category_id = ?''', (access, user_id, category_id)
    )


def is_user_in(user_id: int, category_id: int) -> bool:
    data = read_query(
        '''SELECT COUNT(*) FROM users_categories_permissions 
        WHERE user_id = ? AND category_id = ?''', (user_id, category_id,)
    )
    return data[0][0] > 0


def add_user(user_id: int, category_id: int):
    insert_query('INSERT INTO users_categories_permissions(user_id,category_id) VALUES(?,?)',
                 (user_id, category_id))


def remove_user(user_id: int, category_id: int):
    update_query('DELETE FROM users_categories_permissions WHERE user_id = ? AND category_id = ?',
                 (user_id, category_id,))


def has_write_access(user_id: int, category_id: int):
    return any(read_query(
        '''SELECT 1
           FROM users_categories_permissions
           WHERE user_id = ? AND category_id = ? AND write_access = ?''',
        (user_id, category_id, 1))
    )


def get_privileged_users(category_id):
    data = read_query(
        '''SELECT ucp.user_id, u.username, ucp.write_access
        FROM users_categories_permissions as ucp JOIN users as u
        WHERE ucp.category_id = ?''', (category_id,)
    )
    if data:
        return data


def response_obj_privileged_users(category: Category, users: list[tuple]):
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


def get_topics_by_cat_id(category_id: int):
    data = read_query(
        '''SELECT t.topic_id, t.title, t.user_id, u.username, t.is_locked, t.best_reply_id, t.category_id, c.name
               FROM topics t 
               JOIN users u ON t.user_id = u.user_id
               JOIN categories c ON t.category_id = c.category_id WHERE t.category_id = ?''', (category_id,))

    if data:
        return [TopicResponse.from_query(*row) for row in data]
