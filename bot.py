from random import sample

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Bot
)
import logging
from tables import db_session
from tables.user import User, Tables

AUTORIZATION, TRY_LOGIN, CHOOSING, CHOOSE = range(4)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

bot = Bot('1784466713:AAF6v8fucNKd1nDh0STyIrw-voAm6r-6Hxs')

reply_keyboard = [
    ["Ближайшие задания", "Рандомные задания"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

edit_keyboard = [["Выполнено", "Удалить"]]
edit = ReplyKeyboardMarkup(edit_keyboard, one_time_keyboard=False, resize_keyboard=True)


def start(update, context):
    user_name = update.message.chat.id
    print(user_name)
    if connection(user_name):
        update.message.reply_text('Выберите действие, для продолжения работы', reply_markup=markup)
    else:
        update.message.reply_text("Пришлите токен для входа в аккаунт")
        return TRY_LOGIN


def try_login(update, context):
    user_name = update.message.chat.id
    text = update.message.text
    answer = user_bot(text, user_name)
    if answer:
        print("OK")
        update.message.reply_text('Выберите действие, для продолжения работы', reply_markup=markup)
    else:
        update.message.reply_text("Токен неверный, повторите попытку")
        return TRY_LOGIN


def connection(name):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.connection == str(name)):
        if user.connection == str(name):
            db_sess.close()
            return True
        return False


def user_bot(text, user_name):
    db_sess = db_session.create_session()
    for user in db_sess.query(User).filter(User.token == str(text)):
        if user.token == text:
            user.connection = user_name
            db_sess.commit()
            db_sess.close()
            return True
        return False


def stop(update, context):
    update.message.reply_text("Лады")


def tomorrow(update, context):
    user_name = update.message.chat.id
    db_sess = db_session.create_session()
    user = list(db_sess.query(User).filter(User.connection == user_name))[0]
    lst = list(user.table.filter(Tables.completed == False))[0:6]
    schedule = []
    for homework in lst:
        print(homework.id)
        schedule.append([InlineKeyboardButton(f"{homework.title}", callback_data=f'{homework.id} {user_name}')])
    reply_keyboard = InlineKeyboardMarkup(schedule)
    if len(lst) == 0:
        update.message.reply_text("Тут пока-что пусто")
    else:
        update.message.reply_text("Выберите запись:", reply_markup=reply_keyboard)


def random_homework(update, context):
    user_name = update.message.chat.id
    db_sess = db_session.create_session()
    user = list(db_sess.query(User).filter(User.connection == user_name))[0]
    print(user.id)
    lst = list(user.table.filter(Tables.completed == False))
    schedule = []
    if len(lst) > 3:
        for i in sample(lst, 3):
            print(i.id)
            schedule.append([InlineKeyboardButton(f"{i.title}", callback_data=f'{i.id} {user_name}')])
    elif 0 < len(lst) <= 3:
        for i in sample(lst, len(lst)):
            schedule.append([InlineKeyboardButton(f"{i.title}", callback_data=f'{i.id} {user_name}')])
    if len(lst) == 0:
        update.message.reply_text("Тут пока-что пусто")
    else:
        keyboard = InlineKeyboardMarkup(schedule)
        update.message.reply_text("Выберите запись:", reply_markup=keyboard)


def homework(update, context):
    query = update.callback_query
    text, user = query.data.split(" ")
    db_sess = db_session.create_session()
    table = db_sess.query(Tables).get(int(text))
    schedule = [[(InlineKeyboardButton("Удалить", callback_data=f'Удалить {text}')),
                 (InlineKeyboardButton("Выполнить", callback_data=f'Выполнено {text}'))]]
    keyboard = InlineKeyboardMarkup(schedule)
    query.edit_message_text(f"{table.title}"
                            f"\nТекст: {table.homework_text}"
                            f"\nДедлайн: {table.day} {table.time}")
    for i in table.homework_img:
        img = open(f"static/images/{table.owner_id}/{i.hash}", mode='rb')
        bot.send_photo(chat_id=int(user), photo=img)
    bot.send_message(chat_id=int(user), text="Выберите действие", reply_markup=keyboard)


def record_delete(update, context):
    query = update.callback_query
    _, user = query.data.split()
    db_sess = db_session.create_session()
    table = db_sess.query(Tables).get(int(user))
    title = table.title
    db_sess.delete(table)
    db_sess.commit()
    db_sess.close()
    query.edit_message_text(f'Запись: "{title}" удалена')


def done(update, context):
    query = update.callback_query
    _, user = query.data.split()
    db_sess = db_session.create_session()
    table = db_sess.query(Tables).get(int(user))
    title = table.title
    table.completed = True
    db_sess.commit()
    db_sess.close()
    query.edit_message_text(f'Запись: "{title}" добавлена в архив')


def main():
    updater = Updater('1784466713:AAF6v8fucNKd1nDh0STyIrw-voAm6r-6Hxs', use_context=True)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            # Добавили user_data для сохранения ответа.
            TRY_LOGIN: [MessageHandler(Filters.text, try_login, pass_user_data=True)]
        },
        fallbacks=[MessageHandler(Filters.regex("^Stop&"), stop)]
    )

    # Команды бота
    dispatcher.add_handler(CallbackQueryHandler(done, pattern="Выполнено"))
    dispatcher.add_handler(CallbackQueryHandler(record_delete, pattern="Удалить"))
    dispatcher.add_handler(CallbackQueryHandler(homework))

    dispatcher.add_handler(MessageHandler(Filters.regex('^Ближайшие задания$'), tomorrow))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Рандомные задания$'), random_homework))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    db_session.global_init("db/db.db")
    main()
