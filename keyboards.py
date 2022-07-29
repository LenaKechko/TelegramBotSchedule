from telebot import types


def view_keyboard(bot, message, resp, mess=""):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = [types.KeyboardButton(text=r[0]) for r in resp]
    markup.add(*item)
    markup.add("Back")
    bot.send_message(message.chat.id,
                     mess.format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)
    return markup
