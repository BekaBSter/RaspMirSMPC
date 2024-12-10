from datetime import datetime

import mariadb

import http_requests

from Settings import DB_USER, DB_PORT, DB_HOST, DB_DATABASE, DB_PASSWORD, DEBUG


def connect():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE
        )
        cur = conn.cursor()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return 0, 0
    return conn, cur


def disconnect(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


def db_connection(func):
    def wrapper(*args, **kwargs):
        conn, cur = connect()
        if not conn:
            print("Database connection failed.")
            return None
        try:
            result = func(*args, cur=cur, conn=conn, **kwargs)
        finally:
            disconnect(conn, cur)
        return result
    return wrapper


@db_connection
def search_in_database(chat_id, cur, *args, **kwargs):
    QUERY = f"SELECT user_choice FROM users WHERE chat_id = {chat_id}"
    cur.execute(QUERY)
    user_choice = cur.fetchone()
    if user_choice is None:
        isFind = False
        user_choice = 0
    else:
        isFind = True
        user_choice = user_choice[0]
    return isFind, user_choice


@db_connection
def write_new_user(chat_id, user_name, user_choice, cur, *args, **kwargs):
    cur.execute(f"SELECT MAX(id) FROM users")
    max_id = cur.fetchone()[0]
    if max_id is None:
        user_id = 0
    else:
        user_id = int(max_id) + 1
    time = str(datetime.now())
    cur.execute(
        "INSERT INTO users (id, chat_id, user_name, user_choice, create_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, chat_id, user_name, user_choice, str(time))
    )
    content = str(http_requests.create_content(user_choice))
    cur.execute(
        "INSERT INTO users_content (id, chat_id, content, time) VALUES (?, ?, ?, ?)",
        (user_id, chat_id, content, time)
    )


@db_connection
def rewrite_content_user(chat_id, content, cur, *args, **kwargs):
    try:
        time = str(datetime.now())
        cur.execute(
            """
            UPDATE users_content SET content = ?, time = ? where chat_id = ?
            """,
            (content, time, chat_id)
        )
    except mariadb.ProgrammingError as err:
        print(err)


@db_connection
def remove_user(chat_id, cur, *args, **kwargs):
    try:
        cur.execute(f"DELETE FROM users WHERE chat_id={chat_id}")
        cur.execute(f"DELETE FROM users_content WHERE chat_id={chat_id}")
    except mariadb.Error as err:
        print(f"Error: {err}")


@db_connection
def all_users(cur, *args, **kwargs):
    try:
        cur.execute("SELECT chat_id, user_choice FROM users")
        users = cur.fetchall()
        cur.execute("SELECT content FROM users_content")
        contents = cur.fetchall()
        users_contents = []
        for i in range(0, len(users)):
            users_contents.append([users[i], contents[i]])
        return users_contents
    except IndexError as e:
        print(f"Ошибка {e}")
        return 1


@db_connection
def test_user(cur, *args, **kwargs):
    try:
        cur.execute("SELECT chat_id, user_choice FROM users WHERE chat_id='558710006'")
        users = cur.fetchall()
        cur.execute("SELECT content FROM users_content WHERE chat_id='558710006'")
        contents = cur.fetchall()
        users_contents = []
        for i in range(0, len(users)):
            users_contents.append([users[i], contents[i]])
        return users_contents
    except IndexError as e:
        print(f"Ошибка {e}")
        return 1
