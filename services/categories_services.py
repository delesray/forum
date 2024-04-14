from data.models import Category, StatusCode
from data.database import read_query, update_query, insert_query
from helpers import helpers


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
    data = insert_query(
        'INSERT INTO categories(name) VALUES(?)',
        (category.name,)
    )
    if not isinstance(data, int):
        error_msg = helpers.humanize_error_msg(data)
        return error_msg, StatusCode.BAD_REQUEST

    generated_id = data
    return f'Category {generated_id} was successfully created!', StatusCode.OK


def update(old, new):
    return None
