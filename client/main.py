import commands.category as categories
import commands.users as users
from storage import TokenStorage


def welcome_prompt():
    print('Welcome')
    # token = TokenStorage.get_token()
    # if not token:
    #     print('Hello, please [L]ogin or [R]egister')
    #     choice = input().upper()
    #     if choice == 'L':
    #         users.login()
    #     elif choice == 'R':
    #         users.register()
    #     else:
    #         welcome_prompt()  # you must log in!
    # else:
    #     print('Hello, ', end='')
    #     users.info(token)


def main():
    welcome_prompt()
    while True:
        print('\n[C]ategories / [T]opics / [U]sers / [O]rders / [L]ogin / ')
        choice = input().upper()

        if choice == 'C':
            categories.select_action()
        # elif choice == 'T':
        #     topics.select_action()
        elif choice == 'U':
            users.select_action()
        elif choice == 'OUT':
            users.logout()
        else:
            print("No such command")


if __name__ == '__main__':
    main()
