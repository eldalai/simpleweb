import os
import pyodbc
from functools import wraps

DB_AS400_USER = os.environ.get('DB_AS400_USER')
DB_AS400_PASS = os.environ.get('DB_AS400_PASS')
DB_AS400_HOST = os.environ.get('DB_AS400_HOST')


def connect(username, password):
    conn_str = (
        "DRIVER={IBM i Access ODBC Driver};"
        f"SYSTEM={DB_AS400_HOST};"
        f"UID={username};"
        f"PWD={password};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(e)
        raise e


def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if (
            len(args) >= 2 and
            isinstance(args[0], pyodbc.Cursor) and
            isinstance(args[1], pyodbc.Connection)
        ):
            return func(*args, **kwargs)

        conn = connect(DB_AS400_USER, DB_AS400_PASS)
        try:
            cursor = conn.cursor()
            result = func(cursor, conn, *args, **kwargs)
        except Exception as e:
            print(e)
            raise e
        finally:
            conn.close()
        return result
    return wrapper
