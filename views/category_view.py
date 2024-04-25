from data.models import Category


def priviliged_users_view(category: Category, users: list[tuple]):
    # todo test the sort
    # users = list(sorted(users, key=lambda x: -x[-1]))
    users_dict = {}
    for uid, username, access in users:
        users_dict[uid] = f'{username}: {'write' if access else 'read'} access'

    return {
        'category': category.name,
        'users': users_dict
    }
