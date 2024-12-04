from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException

import database
import http_requests
import Settings
from htmltopng import html_to_png

bot = AsyncTeleBot(Settings.bot_TOKEN)

choices = {"g": "Группа", "t": "Преподаватель", "a": "Аудитория"}
options = ["Смена выбора", "Удалить синхронизацию", "Выход"]


def generate_confirm_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Подтвердить", callback_data="confirm"))
    markup.add(types.InlineKeyboardButton("Отмена", callback_data="cancel"))
    return markup


def generate_choice_markup():
    markup = types.InlineKeyboardMarkup()
    for choice in choices:
        markup.add(types.InlineKeyboardButton(choices[choice], callback_data=f"choice_{choice}"))
    return markup


def generate_options_markup():
    markup = types.InlineKeyboardMarkup()
    for i, option in enumerate(options):
        markup.add(types.InlineKeyboardButton(option, callback_data=f"option_{i}"))
    return markup


def generate_list_markup(choice_type, i=0, prev=False):
    req = http_requests.lists_values[choice_type]
    markup = types.InlineKeyboardMarkup()
    if not prev:
        if i + 10 < len(req):
            j = i + 10
        else:
            j = len(req)
    else:
        if i - 10 >= 0:
            j = i
            i -= 10
        else:
            i = 0
            j = min(10, len(req))
    for choice_id in range(i, j):
        markup.add(
            types.InlineKeyboardButton(
                req[choice_id][0],
                callback_data=f"list_{choice_type}_{choice_id}")
        )
    if j < len(req):
        markup.add(types.InlineKeyboardButton("Далее", callback_data=f"next_{choice_type}_{j}"))
    if i > 0:
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f"next_prev_{choice_type}_{i}"))
    return markup


async def send_message(chat_id, user_choice, file_name_last, file_name_differences, new_content):
    choice_type = user_choice.split("_")[0]
    choice_name = user_choice.split("_")[1]
    id_choice = http_requests.search_id_in_name(choice_type, choice_name)
    value_choice = http_requests.lists_values[choice_type][id_choice][0]
    try:
        await bot.send_message(chat_id,
                               f"Внимание! Изменение расписания для:\n{choices[choice_type]}, {value_choice}\n")
        await bot.send_document(chat_id,
                                document=open(file_name_last, "rb"),
                                visible_file_name="Старое расписание.png")
        await bot.send_document(chat_id,
                                document=open(file_name_differences, "rb"),
                                visible_file_name="Изменения расписания.png")
        database.rewrite_content_user(chat_id, new_content)
        print(f"Пользователю {chat_id} было выслано сообщение без ошибок.\nРабота продолжается")
    except ApiTelegramException as err:
        print(f"{err}"
              f"\nОшибка: пользователь заблокирован! Пользователь будет удален из базы данных!"
              f"\nРабота продолжается")
        database.remove_user(chat_id)


# async def send_admin_message(error):
#    await bot.send_message(6493307161, f"Внимание! Ошибка: {error}")


@bot.message_handler(commands=["start"])
async def start(message):
    chat_id = message.chat.id
    message_id = message.message_id
    await bot.delete_message(chat_id, message_id)
    if not database.search_in_database(chat_id)[0]:
        markup = generate_choice_markup()
        await bot.send_message(message.chat.id, "Выбери:", reply_markup=markup)
    else:
        markup = generate_options_markup()
        await bot.send_message(message.chat.id, "Настройки:", reply_markup=markup)


@bot.message_handler(content_types=["text"])
async def start_text(message):
    await start(message)


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
                                    'location', 'contact', 'sticker'])
async def any_file(message):
    file = None
    match message.content_type:
        case "audio":
            file = "Крутая песня!)"
        case "photo":
            file = "Крутая фотка!)"
        case "voice":
            file = "Не слышно, повтори ещё раз..."
        case "video":
            file = "Крутой видос!)"
        case "document":
            file = "Не умею читать..."
        case "location":
            file = "Далековато ты..."
        case "contact":
            file = "Это кто?"
        case "sticker":
            file = "Класс!)"
    await bot.reply_to(message, f"{file}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("choice_"))
async def callback_choice_inline(call):
    choice_type = call.data.split("_")[1]
    markup = generate_list_markup(choice_type)
    await bot.edit_message_text(
        f"Выберите {choices[choice_type]}:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("option_"))
async def callback_option_inline(call):
    choice_index = int(call.data.split("_")[1])
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    match choice_index:
        case 0:  # Смена выбора
            database.remove_user(str(chat_id))
            markup = generate_choice_markup()
            await bot.edit_message_text("Выбери:", chat_id, message_id, reply_markup=markup)
        case 1:  # Удаление синхронизации
            markup = generate_confirm_markup()
            await bot.edit_message_text("Вы уверены?", chat_id, message_id, reply_markup=markup)
        case 2:  # Отмена
            await bot.delete_message(chat_id, message_id)


@bot.callback_query_handler(func=lambda call: call.data in ["confirm", "cancel"])
async def callback_confirm(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    match call.data:
        case "confirm":
            database.remove_user(str(chat_id))
            await bot.edit_message_text("Синхронизация удалена", chat_id, message_id)
        case "cancel":
            await bot.delete_message(chat_id, message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("list_"))
async def choice_from_list(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, choice_type, choice_id = call.data.split("_")
    choice_name = http_requests.lists_values[choice_type][int(choice_id)][0]
    database.write_new_user(
        int(chat_id),
        str(call.from_user.first_name),
        choice_type + "_" + choice_name,
    )
    await bot.edit_message_text(
        f"Вы выбрали: {choices[choice_type]}, "
        f"{http_requests.lists_values[choice_type][int(choice_id)][0]}",
        chat_id, message_id
    )
    markup = types.InlineKeyboardMarkup(). \
        add(types.InlineKeyboardButton("Да", callback_data="test_yes")). \
        add(types.InlineKeyboardButton("Нет", callback_data="test_no"))
    await bot.send_message(chat_id, "Хотите получить текущее расписание?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("next_"))
async def next_list(call):
    if call.data.split("_")[1] != "prev":
        i = 1
        s = 2
        prev = False
    else:
        i = 2
        s = 3
        prev = True
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    choice_type = call.data.split("_")[i]
    j = int(call.data.split("_")[s])
    markup = generate_list_markup(choice_type, j, prev)
    await bot.edit_message_text("Выберите:", chat_id, message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("test_"))
async def first_test(call):
    option = call.data.split("_")[1]
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id, message_id)
    match option:
        case "yes":
            _, user_choice = database.search_in_database(chat_id)
            content = http_requests.create_content(user_choice)
            file_name_test = f"./files/{chat_id}_test.png"
            html_to_png(content, file_name_test)
            await bot.send_message(chat_id, f"Текущее расписание:")
            await bot.send_document(
                chat_id,
                document=open(file_name_test, "rb"),
                visible_file_name="Текущее расписание.png"
            )
        case "no":
            pass
