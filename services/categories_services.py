from data.models import Category, StatusCode
from data.database import read_query, update_query, insert_query
from helpers import helpers


def get_all():
    data = read_query(
        '''SELECT category_id, name, is_locked, is_private
        FROM categories''')

    categories = [Category.from_query(*row) for row in data]
    return categories


def get_by_id(id):
    return None


def create(category):
    return None


def update(old, new):
    return None
