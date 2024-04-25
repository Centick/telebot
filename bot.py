# import telegram.exp
import telebot
from telebot import types
import sqlite3


# токен бота
TOKEN = "6950767291:AAEYwZRb6r8KPN1uc45-p08pfLD0ps6ZqN4"
bot = telebot.TeleBot(TOKEN)

# подключаем базу данных
con = sqlite3.connect("db.sqlite")
cur = con.cursor()
result = cur.execute("""SELECT * FROM thems""").fetchall()
con.close()

# классы и их темы
classes = {
    "5 класс": [],
    "6 класс": [],
    "7 класс": [],
}

# все темы
topics_info = {}

for i in result:
    if i[4] == "5":
        classes["5 класс"].append(i[1])
    elif i[4] == "6":
        classes["6 класс"].append(i[1])
    elif i[4] == "7":
        classes["7 класс"].append(i[1])

    topics_info[i[1]] = [i[2], i[-2]]

# функци старт
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_class = types.KeyboardButton(text="Выбрать класс")
    button_help = types.KeyboardButton(text="Помощь")
    button_error = types.KeyboardButton(text="Написать об ошибке")
    keyboard.add(button_class, button_help, button_error)
    bot.send_message(chat_id, 'Добро пожаловать. Я вам помогу повторить математику. 😊', reply_markup=keyboard)

# Словарь для хранения предыдущих действий каждого пользователя
user_actions = {}

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    if message.text == "Выбрать класс":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for class_name in classes.keys():
            button_class = types.KeyboardButton(text=class_name)
            keyboard.add(button_class)

        button_back = types.KeyboardButton(text="Назад")
        keyboard.add(button_back)
        bot.send_message(chat_id, "Выберите класс:", reply_markup=keyboard)
        user_actions[chat_id] = "main_menu"

    elif message.text in classes.keys():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for topic in classes[message.text]:
            button_topic = types.KeyboardButton(text=topic)
            keyboard.add(button_topic)
        button_back = types.KeyboardButton(text="Назад")
        keyboard.add(button_back)
        bot.send_message(chat_id, f"Темы для класса {message.text}:", reply_markup=keyboard)
        user_actions[chat_id] = message.text

    elif message.text in topics_info.keys():
        info_text = topics_info[message.text][0]
        photo = open(f"img/{topics_info[message.text][1]}", "rb")
        bot.send_photo(chat_id, photo, info_text)
        user_actions[chat_id] = f"topics_{message.text}"  # Сохраняем текущую выбранную тему

    elif message.text == "Назад":
        if chat_id in user_actions.keys():
            if user_actions[chat_id] == "main_menu":
                start(message)
            elif user_actions[chat_id].startswith("topics_"):
                class_name = user_actions[chat_id][7:]
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for topic in classes[class_name]:
                    button_topic = types.KeyboardButton(text=topic)
                    keyboard.add(button_topic)
                button_back = types.KeyboardButton(text="Назад")
                keyboard.add(button_back)
                bot.send_message(chat_id, f"Темы для {class_name}:", reply_markup=keyboard)
                user_actions[chat_id] = class_name

    elif message.text == "Написать об ошибке":
        chat_id = message.chat.id
        keyboard2 = types.InlineKeyboardMarkup()
        button_helpp = types.InlineKeyboardButton(text="Написать", url="https://web.telegram.org/a/#1259255139")
        keyboard2.add(button_helpp)
        bot.send_message(chat_id, 'Вы можете обратиться к администратору со своим вопросом', reply_markup=keyboard2)

    elif message.text == "Помощь":
        bot.send_message(chat_id, 'Этот бот создан для упрощения обучения математики.'
                                  ' Для повторения темы вы должны в "Меню" нажать "Выбрать класс".'
                                  ' Далее выбрать касс и тему.'
                                  ' Бот выдаст картинку и текст по теме. Хорошего обучения 🥸')


@bot.message_handler(content_types=['text'])
def repeat_all_message(message):
    print(message.text)

bot.polling()
