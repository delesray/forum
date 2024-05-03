from mariadb import connect
from mariadb.connections import Connection
from hidden import database_password


def _get_connection() -> Connection:
    return connect(
        user='root',
        password=database_password,
        host='localhost',
        port=3306,
        database='forum'
    )


def read_query(sql: str, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return list(cursor)


def insert_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.lastrowid


def update_query(sql: str, sql_params=()) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return True


def query_count(sql: str, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return cursor.fetchone()[0]


# todo discuss
def initial_data_seed():
    if query_count('SELECT COUNT(*) from categories') == 0:
        print('Inserting categories')
        insert_query("""INSERT INTO categories(name) VALUES 
                        ('Uncategorized')
                        """)

    if query_count('SELECT COUNT(*) from users') == 0:
        print('Inserting users')
        insert_query(
            """INSERT INTO users(username, password, email, is_admin) VALUES 
            ('admin', '$2b$12$snZATHX9lsgnazHFCtW1tuU9FYuGOnQlwKBeTFmIjx3Y.RZF0MNCS', 'admin@gmail.com', true)""")


def additional_data_seed():
    print('Inserting categories')
    insert_query("""INSERT INTO categories(name) VALUES ('NEW')""")
