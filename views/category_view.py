from data.models import Category


def priviliged_users_view(category: Category, users: list[tuple]):
    # todo test the sort
    # users = list(sorted(users, key=lambda x: -x[-1]))
    users_dict = {}
    for uid, username, is_admin in users:
        users_dict[uid] = f'{username}: {'admin' if is_admin ==  1 else 'regular'} user'
    return {
        'category': category.name,
        'users': users_dict
    }
