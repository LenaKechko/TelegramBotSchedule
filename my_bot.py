import telebot
import psycopg2
import keyboards as kb

bot = telebot.TeleBot('1220511535:AAEuCC_x7AH_2pNIlxxIrAdkWirdRIZQ_GQ')

conn = psycopg2.connect(dbname='schedule', user='postgres', password='pass', host='localhost')
cursor = conn.cursor()
gr = ""
myFaculty = ""
id_facul = 0
state_menu = []


def check_menu(main_menu=False, faculty_menu=False, group_menu=False, day_menu=False, search_menu=False, teacher_menu=False):
    global state_menu
    state_menu = [main_menu, faculty_menu, group_menu, day_menu, search_menu, teacher_menu]


check_menu(main_menu=True)


@bot.message_handler(func=lambda message: 'Back' == message.text, content_types=['text'])
def handle_text(message):
    global state_menu
    if state_menu[0]:
        bot.send_message(message.chat.id,
                         "Возвращаться некуда, только вперед!")
    elif state_menu[1] or state_menu[4] or state_menu[5]:
        check_menu(main_menu=True)
        message.text = '/start'
        welcome(message)
    elif state_menu[2]:
        message.text = '🎲 Выбрать факультет'
        check_menu(faculty_menu=True)
        menu_faculty(message)
    elif state_menu[3]:
        message.text = myFaculty
        check_menu(group_menu=True)
        menu_group(message)


@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    resp = [("🎲 Выбрать факультет",), ("Найти преподавателя",), ("😊 Обратная связь",)]
    # resp.append()
    # resp.append()
    kb.view_keyboard(bot, message, resp, "Добро пожаловать, {0.first_name}! Я - бот <b>{1.first_name}</b>.\n "
                                         "Бот, созданный для того, чтобы ты, мой дорогой друг, всегда был в курсе "
                                         "своего расписания!")


@bot.message_handler(func=lambda message: state_menu[0], content_types=['text'])
def menu_faculty(message):
    global state_menu
    if message.chat.type == 'private':
        if message.text == '🎲 Выбрать факультет':
            # keyboard
            check_menu(faculty_menu=True)
            cursor.execute("select faculty from faculty")
            resp_faculty = cursor.fetchall()
            kb.view_keyboard(bot, message, resp_faculty, "{0.first_name}, выбери свой факультет!")
        elif message.text == '😊 Обратная связь':
            bot.send_message(message.chat.id,
                             "Если ты обнаружил какие-то проблемы при использовании бота или хочешь помочь "
                             "в разработке, вот мой создатель - @mitsukanov.\n Напиши ему!")
        elif message.text == 'Найти преподавателя':
            hide_markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id,
                             "{0.first_name}, введите ФИО или ее часть, и нажмите ввод! Регистр букв имеет значение.".format(
                                 message.from_user, bot.get_me()),
                             parse_mode='html', reply_markup=hide_markup)
            check_menu(search_menu=True)
        else:
            bot.send_message(message.chat.id, "Не верный вариант!")


@bot.message_handler(func=lambda message: state_menu[1], content_types=['text'])
def menu_group(message):
    global state_menu, myFaculty, id_facul
    # проверяем выбран ли факультет
    cursor.execute("select * from faculty where faculty = %s", (message.text,))
    resp = cursor.fetchall()
    if resp:
        id_facul = resp[0][0]
        myFaculty = resp[0][1]
        cursor.execute("select group_name from groupa where id_faculty = %s", (id_facul,))
        resp_group = cursor.fetchall()
        kb.view_keyboard(bot, message, resp_group, "{0.first_name}, выбери группу!")
        check_menu(group_menu=True)
    else:
        bot.send_message(message.chat.id, "Введите корректно факультет!")


@bot.message_handler(func=lambda message: state_menu[2], content_types=['text'])
def menu_day(message):
    global gr, id_facul
    global state_menu
    # проверяем выбрана ли группа
    cursor.execute("select * from groupa where group_name = %s and id_faculty = %s", (message.text, id_facul,))
    resp = cursor.fetchall()
    if resp:
        gr = resp[0][1]
        cursor.execute("select dayofweek from dayofweek")
        resp_day = cursor.fetchall()
        kb.view_keyboard(bot, message, resp_day, "{0.first_name}, выбери день недели")
        check_menu(day_menu=True)
    else:
        bot.send_message(message.chat.id, "Нет группы или не из того факультета!")


@bot.message_handler(func=lambda message: state_menu[3], content_types=['text'])
def last_day(message):
    cursor.execute("select dayofweek from dayofweek where dayofweek = %s", (message.text,))
    resp = cursor.fetchall()
    if resp:
        day = resp[0][0]
        # Выполняем запрос.
        cursor.execute("select hours, name_disc, fio, number, corpus "
                       "from bell, disc, teachers, audit, groupa, dayofweek, corpus, raspisanie "
                       "where raspisanie.id_group = groupa.id and raspisanie.id_dow = dayofweek.id and "
                       "raspisanie.id_time = bell.id and raspisanie.id_disc = disc.id and "
                       "corpus.id = audit.id_corpus and "
                       "raspisanie.id_teacher = teachers.id and raspisanie.id_audit = audit.id and "
                       "group_name = %s and dayofweek = %s", (gr, day,))
        resp = cursor.fetchall()
        if resp:
            result = ""
            for r in resp:
                result += ("\n{0} \n ауд. {3}, копр. {4}\n{2}\n{1}\n".format(r[0], r[1], r[2], r[3], r[4]))
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "Пар нет! Гуляем! Тыц-тыц!")
    else:
        bot.send_message(message.chat.id, "Не верный день!")


@bot.message_handler(func=lambda message: state_menu[4], content_types=['text'])
def menu_teacher(message):
    cursor.execute("select fio from teachers "
                   "where fio like '%{}%'".format(message.text))
    resp_teacher = cursor.fetchall()
    if resp_teacher:
        kb.view_keyboard(bot, message, resp_teacher, "{0.first_name}, выбери преподавателя!")
        check_menu(teacher_menu=True)
    else:
        bot.send_message(message.chat.id, "Нет такого преподавателя или не верно введено ФИО!")


@bot.message_handler(func=lambda message: state_menu[5], content_types=['text'])
def last_menu_teacher(message):
    cursor.execute("select fio from teachers where fio = %s", (message.text,))
    resp = cursor.fetchall()
    if resp:
        fio = resp[0][0]
        # Выполняем запрос.
        cursor.execute("select dayofweek, hours, group_name, name_disc, number, corpus "
                       "from bell, disc, teachers, audit, groupa, dayofweek, corpus, raspisanie "
                       "where raspisanie.id_group = groupa.id and raspisanie.id_dow = dayofweek.id and "
                       "raspisanie.id_time = bell.id and raspisanie.id_disc = disc.id and "
                       "corpus.id = audit.id_corpus and "
                       "raspisanie.id_teacher = teachers.id and raspisanie.id_audit = audit.id and "
                       "fio = %s", (fio,))
        resp_rasp = cursor.fetchall()
        if resp_rasp:
            result = ""
            for r in resp_rasp:
                result += ("\n{0} \n{1} \n{2} \n{3} \nауд. {4}, копр. {5}\n".format(r[0],
                                                                                     r[1], r[2], r[3], r[4], r[5]))
            bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "А может у преподавателя отпуск?")
    else:
        bot.send_message(message.chat.id, "Не верно введено ФИО!")


    # Закрываем подключение.
    # cursor.close()
    # conn.close()

# RUN
bot.polling(none_stop=True)
