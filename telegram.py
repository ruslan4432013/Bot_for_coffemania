import telebot
from config import TOKEN
from coffemania import ch_c, ch_b
from telebot import types

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    if message.text == "/start":
        keyboard = types.InlineKeyboardMarkup()
        key_calc = types.InlineKeyboardButton(text='Посчитать часы специалистов', callback_data='calc')
        key_calc_bar = types.InlineKeyboardButton(text='Посчитать часы всех бариста', callback_data='calc_bar')
        key_calc_all = types.InlineKeyboardButton(text='Посчитать часы всех ', callback_data='calc_all')
        keyboard.add(key_calc)
        keyboard.add(key_calc_bar)
        keyboard.add(key_calc_all)
        bot.send_message(message.from_user.id, text='Привет!', reply_markup=keyboard)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "calc":
        try:
            ch_c.insert_values('K')
            bot.send_message(call.message.chat.id, "Выполнено")
        except:
            bot.send_message(call.message.chat.id, "Что-то пошло не так, проверьте таблицу")
    elif call.data == 'calc_bar':
        try:
            ch_b.insert_values('I')
            bot.send_message(call.message.chat.id, "Выполнено")
        except:
            bot.send_message(call.message.chat.id, "Что-то пошло не так, проверьте таблицу")
    elif call.data == 'calc_all':
        try:
            ch_c.insert_values('K')
            ch_b.insert_values('I')
            bot.send_message(call.message.chat.id, "Выполнено")
        except Exception as exp:
            bot.send_message(call.message.chat.id, f"Что-то пошло не так, проверьте таблицу {exp}")


bot.polling(none_stop=True, interval=0)
