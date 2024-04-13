from mariadb import connect
import mariadb
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
        try:
            cursor.execute(sql, sql_params)
            conn.commit()
        except mariadb.Error as e:
            return e

        return cursor.lastrowid


def update_query(sql: str, sql_params=()) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

    return True
