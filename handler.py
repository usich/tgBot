from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton

from bot import bot, dp
from dbconn import cursor, conn
from get_data import check_backup_local, check_backup_yadisk


async def handler():
    class Form(StatesGroup):
        message = State()

    @dp.message_handler(state=Form.message)
    async def process_message(message: types.Message, state: FSMContext):

        await state.finish()

        cursor.execute("SELECT chat_id from users  WHERE role <> 'orl'")

        sender = message.from_user.first_name

        for i in cursor.fetchall():
            await bot.send_message(i[0], f"<i>{sender}:</i>\n "
                                         f"{message.text}",
                                   parse_mode=types.ParseMode.HTML)

    @dp.message_handler(commands=['start'])
    async def send_welcome(msg: types.Message):
        cursor.execute(f"SELECT * from users where chat_id = {int(msg.chat.id)}")
        if len(cursor.fetchall()) == 0:
            cursor.execute(f'''INSERT INTO users(user_name, chat_id)
            VALUES("{msg.from_user.first_name}", {msg.chat.id});''')
            conn.commit()
        cursor.execute(f'SELECT chat_id from users where active = 1 and chat_id = {int(msg.chat.id)}')
        temp = len(cursor.fetchall())
        if temp == 0:
            await msg.answer('Приветсвую! ✌️\n'
                             'Функции бота будут доступны, после активации. ☝ \n'
                             'Обратитесь к админу. 🤙')
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            b1 = KeyboardButton('Получить список бэкапов 📥')
            b2 = KeyboardButton('Узнать мой статус 🙈')
            # b3 = KeyboardButton('Инфо о выполненных задачах ✅')
            b4 = KeyboardButton('Отправить сообщение в чат 📨')
            keyboard.add(b1).add(b2).add(b4)

            await msg.answer("Выберете что-нибудь", reply_markup=keyboard)

    @dp.message_handler(content_types=['text'])
    async def get_list_backup(msg: types.Message):
        cursor.execute(f'SELECT chat_id from users where active = 1 and chat_id = {int(msg.chat.id)}')
        temp = len(cursor.fetchall())
        if temp == 0:
            await msg.answer('Приветсвую! ✌️\n'
                             'Функции бота будут доступны, после активации. ☝ \n'
                             'Обратись к админу. 🤙')
            return True
        # if msg.text.lower() == 'инфо о выполненных задачах ✅':
        #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #     b1 = KeyboardButton('Получить список задач за предыдущий месяц 📊')
        #     b2 = KeyboardButton('Получить список задач за последние 5 дней 📊')
        #     b3 = KeyboardButton('Назад ⤴️')
        #     keyboard.add(b1).add(b2).add(b3)
        #
        #     await msg.answer("Выберете период отчета...", reply_markup=keyboard)
        #
        # elif msg.text.lower() == 'назад ⤴️':
        #
        #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #     b1 = KeyboardButton('Получить список бэкапов 📥')
        #     b2 = KeyboardButton('Узнать мой статус 🙈')
        #     b3 = KeyboardButton('Инфо о выполненных задачах ✅')
        #     b4 = KeyboardButton('Отправить сообщение в чат 📨')
        #     keyboard.add(b1).add(b2).add(b3).add(b4)
        #
        #     await msg.answer("Выберете что-нибудь", reply_markup=keyboard)

        if msg.text.lower() == 'получить список бэкапов 📥':
            data = await check_backup_local()
            data_ya = await check_backup_yadisk()
            await msg.answer(data)

            await msg.answer(data_ya)

        elif msg.text.lower() == 'отправить сообщение в чат 📨':
            '''Сообщение которое увидят все участники бота'''
            await Form.message.set()
            await msg.reply('Напишите текст сообщения')

        elif msg.text.lower() == 'узнать мой статус 🙈':
            cursor.execute(f"SELECT * from users where chat_id = {int(msg.chat.id)}")
            result = cursor.fetchall()
            if len(result) == 0:
                await msg.answer('Вас нет в нашей базе данных, обратитесь к админу 🤷')
            else:
                active = result[0][4]
                group = result[0][3]
                await msg.answer(f'❇️<b>Активность:выафыавыф ваыфа</b> <i>{bool(active)}</i> \n\n'
                                 f'❇️<b>Группа:</b> <i>{group}</i>', parse_mode=types.ParseMode.HTML)

        # elif msg.text.lower() == 'получить список задач за предыдущий месяц 📊':
        #
        #     str_prettify = await get_jira_task('every_month')
        #     for i in str_prettify.split('        '):
        #         await msg.answer(i, parse_mode=types.ParseMode.HTML)
        #
        # elif msg.text.lower() == 'получить список задач за последние 5 дней 📊':
        #
        #     str_prettify = await get_jira_task('every_week')
        #     for i in str_prettify.split('        '):
        #         await msg.answer(i, parse_mode=types.ParseMode.HTML)

        else:
            await msg.answer('Не понимаю, что это значит.')
