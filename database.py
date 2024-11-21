from datetime import datetime

import mariadb

import http_requests


def connect():
    try:
        conn = mariadb.connect(
            user="root",
            password="P@ssw0rd",
            host="10.12.50.51",
            port=3306,
            database="bot"
        )
        cur = conn.cursor()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return 0, 0
    return conn, cur


def disconnect(conn):
    conn.commit()
    conn.close()


def search_in_database(chat_id):
    conn, cur = connect()
    cur.execute(f"SELECT user_choice FROM users WHERE chat_id = {chat_id}")
    user_choice = cur.fetchone()
    if user_choice is None:
        isFind = False
        user_choice = 0
    else:
        isFind = True
        user_choice = user_choice[0]
    disconnect(conn)
    return isFind, user_choice


def write_new_user(chat_id, user_name, user_choice):
    conn, cur = connect()
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
    conn.commit()
    content = str(http_requests.create_content(user_choice))
    cur.execute(
        "INSERT INTO users_content (id, chat_id, content, time) VALUES (?, ?, ?, ?)",
        (user_id, chat_id, content, time)
    )
    disconnect(conn)


def rewrite_content_user(chat_id, content):
    conn, cur = connect()
    time = str(datetime.now())
    try:
        cur.execute(
            """
            UPDATE users_content SET content = ?, time = ? where chat_id = ?
            """,
            (content, time, chat_id)
        )
    except mariadb.ProgrammingError as err:
        print(err)
    disconnect(conn)


def remove_user(chat_id):
    conn, cur = connect()
    try:
        cur.execute(f"DELETE FROM users WHERE chat_id={chat_id}")
        cur.execute(f"DELETE FROM users_content WHERE chat_id={chat_id}")
        disconnect(conn)
    except mariadb.Error as err:
        print(f"Error: {err}")


def all_users():
    conn, cur = connect()
    if conn != 0:
        cur.execute("SELECT chat_id, user_choice FROM users")
        users = cur.fetchall()
        cur.execute("SELECT content FROM users_content")
        try:
            contents = cur.fetchall()
        except IndexError:
            return 1
        users_contents = []
        for i in range(0, len(users)):
            users_contents.append([users[i], contents[i]])
        disconnect(conn)
        return users_contents
    else:
        return 1