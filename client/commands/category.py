import requests
from config import BASE_URL
from commands.action import Action

CATEGORIES_URL = f'{BASE_URL}/categories'

# EXAMPLE

# def show_by_id():
#     category_id = int(input('Category id = '))
#     response = requests.get(f'{CATEGORIES_URL}/{category_id}')
#     data = response.json()

#     category = data['category']
#     products = data['products']

#     print(f'==== {category["name"]} ====')
#     for product in products:
#         print(product)


# def show_all():
#     response = requests.get(CATEGORIES_URL)
#     data = response.json()
#     for object in data:
#         category = object['category']
#         products = object['products']

#         print(
#             f'{category["id"]}. {category["name"]} ({len(products)} products)')


# def create_category():
#     name = input('Category name = ')

#     response = requests.post(CATEGORIES_URL, json={'name': name})

#     if response.status_code == 200:
#         id = response.json()['category']['id']
#         print(f'Created category with id {id}')
#     if response.status_code == 400:
#         print(response.text)
#     if response.status_code == 422:
#         print('Invalid model schema:')
#         errors = response.json()['detail']
#         for error in errors:
#             print('-', error['msg'], '->', error['loc'][1])


# def select_action():
#     actions = {
#         'S': Action(show_by_id, requires_login=False, name='[S]ingle'),
#         'A': Action(show_all, requires_login=False, name='[A]ll'),
#         'C': Action(create_category, requires_login=False, name='[C]reate')
#     }

#     print('Select category action?')
#     print(' / '.join(action.name for action in actions.values()))

#     selected_action = input().upper()
#     actions.get(selected_action, Action.default()).execute()
