from data.models import Category
from data.database import read_query, update_query, insert_query
from mariadb import IntegrityError


def get_all():
    data = read_query(
        '''SELECT category_id, name, is_locked, is_private
        FROM categories''')

    categories = [Category.from_query(*row) for row in data]
    return categories


def get_by_id(category_id):
    data = read_query(
        '''SELECT category_id, name, is_locked, is_private
        FROM categories WHERE category_id = ?''', (category_id,))
    if not data:
        return None
    category = Category.from_query(*data[0])
    return category


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


def publicize(category_id: int):
    update_query('UPDATE categories SET is_private = ? WHERE category_id = ?',
                 (False, category_id))


def privatize(category_id: int):
    update_query('UPDATE categories SET is_private = ? WHERE category_id = ?',
                 (True, category_id))
