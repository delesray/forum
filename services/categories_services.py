from data.models import Category
from data.database import read_query, update_query, insert_query


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

    category = [Category.from_query(*row) for row in data]
    if not category:
        return None

    return category[0]


def create(category):
    """
    Creates category without
    Handles unique columns violations with try/except in queries
    """
    request_sent_from_admin = True
    data = insert_query(
        'INSERT INTO categories(name) VALUES(?)',
        (category.name,)
    )
    if not isinstance(data, int):
        error_msg = helpers.humanize_error_msg(data)
        return error_msg, StatusCode.BAD_REQUEST

    generated_id = data
    return f'Category {generated_id} was successfully created!', StatusCode.OK


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

    if data is not True:
        error_msg = helpers.humanize_error_msg(data)
        return error_msg, StatusCode.BAD_REQUEST

    return merged, StatusCode.OK
