import asyncio
import requests
from bs4 import BeautifulSoup as BS

import bot
import database

import os

urls = {
    "g": "https://rasp.mirsmpc.ru/cg.htm",
    "t": "https://rasp.mirsmpc.ru/cp.htm",
    "a": "https://rasp.mirsmpc.ru/ca.htm"
}

lessons_type = {
    "g": ["Журнал занятий", "Расписание аудитории", "Расписание преподавателя"],
    "t": ["Расписание группы", "Расписание аудитории", "Журнал занятий"],
    "a": ["Расписание преподавателя", "Расписание группы", "Журнал занятий"]
}

default_url = "https://rasp.mirsmpc.ru/"

last_time = 0
lists_values = {}


async def check_content():
    global lists_values
    while True:
        lists_values = {
            "g": create_list_values("g"),
            "t": create_list_values("t"),
            "a": create_list_values("a")
        }
        # users_contents = database.all_users()
        users_contents = database.test_user()
        if users_contents != 1:
            # print("Производится проверка таблиц пользователей.")
            for user in users_contents:
                chat_id = user[0][0]
                user_choice = user[0][1]
                new_content = str(create_content(user_choice))
                last_content = str(user[1][0])
                file_name_last = f"files/{chat_id}_last.html"
                file_name_new = f"files/{chat_id}_new.html"
                file_name_differences = f"files/{chat_id}_differences.html"
                if new_content == "1":
                    err = "Ошибка: контент равен 1.\nРабота продолжается."
                    print(err)
                if new_content != last_content and new_content != "1":
                    users_contents.remove(user)
                    try:
                        os.remove(file_name_last)
                        os.remove(file_name_new)
                        os.remove(file_name_differences)
                    except FileNotFoundError:
                        print(f"Нет файла у пользователя {chat_id}.\nРабота продолжается")
                    with open(file_name_differences, "w") as file_differences:
                        file_differences.write(check_differences_content(last_content, new_content))
                    with open(file_name_last, "w") as file_last:
                        file_last.write(last_content)
                    with open(file_name_new, "w") as file_new:
                        file_new.write(new_content)
                    try:
                        await bot.send_message(chat_id, user_choice, file_name_last, file_name_differences, new_content)
                    except():
                        err = f"Пользователю {chat_id} не было выслано новое расписание по какой-то " \
                              f"ошибке.\nРабота продолжается"
                        print(err)
                        # await bot.send_admin_message(err)
            # print("Проверка пользователей окончена.")
        await asyncio.sleep(120)


def create_soup(url):
    try:
        page = requests.get(url)
        page.encoding = "cp1251"
        soup = BS(page.text, "html.parser")
        return soup
    except requests.exceptions.ConnectionError as err:
        err = f"Ошибка при запросе страницы: {err}.\nРабота продолжается."
        print(err)
        return 1


def create_list_values(choice_type):
    url = urls[choice_type]
    soup = create_soup(url)
    if soup != 1:
        elements = soup.find_all(class_='z0', href=True)
        values = []
        for element in elements:
            values.append([element.get_text(), default_url + element["href"]])
        return values
    else:
        return 1


def create_content(user_choice):
    choice_type, choice_name = user_choice.split("_")
    choice_id = search_id_in_name(choice_type, choice_name)
    coding_begin = \
        f'''<!DOCTYPE html>
            <html lang="ru">
            <head>
            <meta charset="CRLF">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{choice_name}</title>
            </head>
            <body>'''
    coding_end = \
        '''</body>
            </html>'''
    if choice_id >= 0:
        try:
            url = lists_values[choice_type][choice_id][1]
            soup = create_soup(url)
        except IndexError as err:
            err = f"{err}. Работа продолжается"
            print(err)
            soup = 1
        if soup != 1:
            content = format_content(soup.find("table", class_="inf"))
            content = coding_begin + "\n" + choice_name + "\n" + content + coding_end
            return content
        else:
            return 1
    else:
        return 1


def format_content(raw_content):
    table_begin = '<table border="0" cellspacing="1" class="inf" width="100%">\n'
    table_end = '</table>'
    replacements = {
        '''onmouseout="this.style.backgroundColor='#FFCF63'" onmouseover="this.style.backgroundColor='#FFDF93'"''': '''style="background-color: #f4d35e;"''',
        '''class="nul"''': '''class="nul" style="background-color: #faf0ca;"''',
        '''class="hd"''': '''class="hd" style="background-color: #0d3b66;"'''
    }
    rows = raw_content.find_all("tr")
    formatted_rows = []
    for row in rows:
        row_str = str(row)
        for original, replacement in replacements.items():
            row_str = row_str.replace(original, replacement)
        formatted_rows.append(row_str)
    ready_content = table_begin + "\n".join(formatted_rows) + "\n" + table_end
    return ready_content


def create_file_from_content(chat_id, content):
    file_name_test = f"files/{chat_id}_test.html"
    with open(file_name_test, "w") as file:
        file.write(str(content))
    return file_name_test


def check_time_in_site(prev_time=0):
    soup = create_soup(default_url + "cp.htm")
    if soup != 1:
        current_time = soup.find(class_="ref").get_text(strip=True).split()[-1][:-1]
        if current_time != prev_time:
            isChange = True
        else:
            isChange = False
        return current_time, isChange
    else:
        return 0, False


def search_id_in_name(choice_type, choice_name):
    if lists_values[choice_type] != 1:
        for i in range(0, len(lists_values[choice_type])):
            name = lists_values[choice_type][i][0]
            if choice_name == name:
                return i
    else:
        return -1


def check_differences_content(last_content, new_content):
    last_content = last_content.split("\n")
    new_content = new_content.split("\n")
    difference_content = ""
    yellow_color = '''style="background-color: #f4d35e'''
    red_color = '''style="background-color: #ff477e'''
    if len(last_content) == len(new_content):
        print("last equal new")
        for i in range(0, len(last_content)):
            if last_content[i] != new_content[i]:
                new_content[i] = new_content[i].replace(yellow_color, red_color)
            difference_content = difference_content + "\n" + new_content[i]
    else:
        print("last not equal new")
        for i in range(0, min(len(last_content), len(new_content))):
            if last_content[i] != new_content[i]:
                new_content[i] = new_content[i].replace(yellow_color, red_color)
            difference_content = difference_content + "\n" + new_content[i]
        for i in range(min(len(last_content), len(new_content)), max(len(last_content), len(new_content))):
            new_content[i] = new_content[i].replace(yellow_color, red_color)
            difference_content = difference_content + "\n" + new_content[i]
    return difference_content
