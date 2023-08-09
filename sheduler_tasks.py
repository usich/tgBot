from aiogram import types

from bot import bot
from dbconn import cursor
from get_data import check_backup_local, check_backup_yadisk
from get_data import get_jira_task


async def task_check_backup_local():
    data = await check_backup_local(True)
    check = False
    message = '⏺ <b>Бэкапы ИБ 1С и сайтов <strong>ЛОКАЛЬНО</strong>:</b> \n\n'
    if data.get('error') is not None:
        message += data.get('error') + '\n\n'
    else:
        for i in data:
            if data.get(i) != 1:
                check = True
                if data.get(i) == 0:
                    message += f'   🔴 {i}: не найден актуальный бэкап \n'
                else:
                    message += f'   🔴 {i}: {data.get(i)} \n'
        if not check:
            message += f'   🟢 Ошибок не обнаружено! ✅'
    cursor.execute("SELECT chat_id from users  WHERE role <> 'orl' and active = 1")
    for i in cursor.fetchall():
        try:
            await bot.send_message(i[0], message, parse_mode=types.ParseMode.HTML)
        except Exception as ex:
            print(i[0])
            print(ex)


async def task_check_backup_ya_disk():
    data = await check_backup_yadisk(True)
    check = False
    message = '⏺ <b>Бэкапы ИБ 1С и сайтов <strong>Yandex Disk</strong>: </b> \n\n'
    for i in data:
        if data.get(i) != 1:
            check = True
            if data.get(i) == 0:
                message += f'   🔴 {i}: не найден актуальный бэкап \n'
            else:
                message += f'   🔴 {i}: {data.get(i)} \n'
    if not check:
        message += f'   🟢 Ошибок не обнаружено! ✅'
    cursor.execute("SELECT chat_id from users  WHERE role <> 'orl' and active = 1")
    for i in cursor.fetchall():
        await bot.send_message(i[0], message, parse_mode=types.ParseMode.HTML)


async def clear_history_chat():
    cursor.execute('SELECT chat_id from users')
    for i in cursor.fetchall():
        bot.delete_message(i[0])


async def task_get_jira(mode):
    str_prettify = await get_jira_task(mode)
    cursor.execute("SELECT chat_id from users WHERE active = 1")
    for i in cursor.fetchall():
        for j in str_prettify.split('        '):
            await bot.send_message(i[0], j, parse_mode=types.ParseMode.HTML)
