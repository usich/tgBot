from get_data import check_backup_local, check_backup_yadisk
from dbconn import cursor, conn
from bot import bot, dp
from aiogram import types
from get_data import get_jira_task


async def task_check_backup_local():
    data = await check_backup_local(True)
    check = False
    message = '🟡 <b>Бэкапы ИБ 1С и сайтов <strong>ЛОКАЛЬНО</strong>:</b> \n\n'
    for i in data:
        if data.get(i) != 1:
            check = True
            if data.get(i) == 0:
                message += f'   🔴 {i}: не найден актуальный бэкап \n'
            else:
                message += f'   🔴 {i}: {data.get(i)} \n'
    if not check:
        message += f'   🟢 Ошибок не обнаружено! ✅'
    cursor.execute("SELECT chat_id from users  WHERE role <> 'orl'")
    for i in cursor.fetchall():
        await bot.send_message(i[0], message, parse_mode=types.ParseMode.HTML)


async def task_check_backup_ya_disk():
    data = await check_backup_yadisk(True)
    check = False
    message = '🟡 <b>Бэкапы ИБ 1С и сайтов <strong>Yandex Disk</strong>: </b> \n\n'
    for i in data:
        if data.get(i) != 1:
            check = True
            if data.get(i) == 0:
                message += f'   🔴 {i}: не найден актуальный бэкап \n'
            else:
                message += f'   🔴 {i}: {data.get(i)} \n'
    if not check:
        message += f'   🟢 Ошибок не обнаружено! ✅'
    cursor.execute("SELECT chat_id from users  WHERE role <> 'orl'")
    for i in cursor.fetchall():
        await bot.send_message(i[0], message, parse_mode=types.ParseMode.HTML)


async def clear_history_chat():
    cursor.execute('SELECT chat_id from users')
    for i in cursor.fetchall():
        bot.delete_message(i[0])


async def task_get_jira(mode):

    str_prettify = await get_jira_task(mode)
    cursor.execute("SELECT chat_id from users")
    for i in cursor.fetchall():
        await bot.send_message(i[0], str_prettify, parse_mode=types.ParseMode.HTML)
