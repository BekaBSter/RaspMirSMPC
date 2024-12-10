from datetime import datetime

import mariadb

import http_requests

from Settings import DB_USER, DB_PORT, DB_HOST, DB_DATABASE, DB_PASSWORD, DEBUG, out


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
        if DEBUG:
            out("База данных: Успешное подключение к базе данных.", "g")
    except mariadb.Error as e:
        out(f"База данных: Ошибка подключения к БД: {e}!", "r")
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
            return None
        try:
            result = func(*args, cur=cur, **kwargs)
        finally:
            disconnect(conn, cur)
        return result
    return wrapper


@db_connection
def search_in_database(chat_id, cur):
    QUERY = f"SELECT user_choice FROM users WHERE chat_id = {chat_id}"
    cur.execute(QUERY)
    user_choice = cur.fetchone()
    if user_choice is None:
        isFind = False
        user_choice = 0
        if DEBUG:
            out(f"База данных: Пользователь в базе данных не найден. User_id: {chat_id}", "r")
    else:
        isFind = True
        user_choice = user_choice[0]
        if DEBUG:
            out(f"База данных: Пользователь найден в базе данных. User_id", "g")
    return isFind, user_choice


@db_connection
def write_new_user(chat_id, user_name, user_choice, cur):
    cur.execute(f"SELECT MAX(id) FROM users")
    max_id = cur.fetchone()[0]
    if max_id is None:
        user_id = 0
    else:
        user_id = int(max_id) + 1
    time = str(datetime.now())
    content = str(http_requests.create_content(user_choice))
    cur.execute(
        "INSERT INTO users (id, chat_id, user_name, user_choice, create_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, chat_id, user_name, user_choice, str(time))
    )
    cur.execute(
        "INSERT INTO users_content (id, chat_id, content, time) VALUES (?, ?, ?, ?)",
        (user_id, chat_id, content, time)
    )
    if DEBUG:
        out(f"База данных: Успешное создание нового пользователя. User_id: {chat_id}, username: {user_id}", "g")


@db_connection
def rewrite_content_user(chat_id, content, cur):
    try:
        time = str(datetime.now())
        cur.execute(
            """
            UPDATE users_content SET content = ?, time = ? where chat_id = ?
            """,
            (content, time, chat_id)
        )
        if DEBUG:
            out(f"База данных: Успешное обновление данных пользователя. User_id: {chat_id}", "g")
    except mariadb.ProgrammingError as e:
        out(f"База данных: Ошибка обновления данных пользователя: {e}. User_id: {chat_id}", "r")


@db_connection
def remove_user(chat_id, cur):
    try:
        cur.execute(f"DELETE FROM users WHERE chat_id={chat_id}")
        cur.execute(f"DELETE FROM users_content WHERE chat_id={chat_id}")
        if DEBUG:
            out(f"База данных: Успешное удаление пользователя. User_id: {chat_id}", "g")
    except mariadb.Error as e:
        out(f"База данных: Ошибка удаления пользователя: {e}. User_id: {chat_id}", "r")


@db_connection
def all_users(cur):
    try:
        cur.execute("SELECT chat_id, user_choice FROM users")
        users = cur.fetchall()
        cur.execute("SELECT content FROM users_content")
        contents = cur.fetchall()
        users_contents = []
        for i in range(0, len(users)):
            users_contents.append([users[i], contents[i]])
        if DEBUG:
            out(f"База данных: Успешное получение данных пользователей.", "g")
        return users_contents
    except IndexError as e:
        out(f"База данных: Ошибка получения данных пользователей: {e}.", "r")
        return 1


@db_connection
def test_user(cur):
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
