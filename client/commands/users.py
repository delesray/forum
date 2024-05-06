import requests
from commands.action import Action
from config import BASE_URL
from storage import TokenStorage

USERS_URL = f'{BASE_URL}/users'


def login():
    data = {
        'username': input('Username = '),
        'password': input('Password = ')
    }

    response = requests.post(f'{USERS_URL}/login', json=data)

    if response.status_code == 200:
        token = response.json()['token']
        TokenStorage.save_token(token)
        print('Successfully logged in.')
    else:
        print('Invalid login attempt')


def logout(token):
    TokenStorage.delete_token()


def info(token):
    response = requests.get(f'{USERS_URL}/info', headers={'x-token': token})

    if response.status_code == 200:
        print(user_view(response.json()))
    else:
        print(response.text)


def register():
    data = {
        'username': input('Username = '),
        'password': input('Password = ')
    }

    response = requests.post(f'{USERS_URL}/register', json=data)
    if response.status_code == 200:
        print('Successfully registered!')
        print(user_view(response.json()))
    else:
        print(response.text)


def show_my_conversations(token):
    pass
    # response = requests.get(f'{USERS_URL}/orders', headers={'x-token': token})
    #
    # orders = response.json()
    # if not orders:
    #     print('You have no orders.')
    # for order in orders:
    #     print(order_view(order))
    #     print('---------------')


def select_action():
    actions = {
        'IN': Action(login, requires_login=False, name='log[IN]'),
        'OUT': Action(logout, requires_login=True, name='log[OUT]'),
        'I': Action(info, requires_login=True, name='[I]nfo'),
        'R': Action(register, requires_login=False, name='[R]egister'),
        'O': Action(show_my_conversations, requires_login=True, name='[C]essages'),
    }

    print('Select user action?')
    print(' / '.join(action.name for action in actions.values()))

    selected_action = input().upper()
    actions.get(selected_action, Action.default()).execute()
