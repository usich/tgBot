import config
import aioschedule
import asyncio
from bot import dp
from handler import handler
from sheduler_tasks import task_check_backup_local, task_check_backup_ya_disk, clear_history_chat, task_get_jira
import datetime


async def main():

    await handler()

    async def get_day():
        day_of_month = datetime.datetime.now().day
        if day_of_month == 11:
            await task_get_jira('every_month')

    async def scheduler():
        aioschedule.every().day.at(config.time_to_run.get('backup')).do(task_check_backup_local)
        aioschedule.every().day.at(config.time_to_run.get('backup')).do(task_check_backup_ya_disk)
        aioschedule.every().day.at(config.time_to_run.get('send_list_task_month')).do(get_day)
        aioschedule.every().friday.at(config.time_to_run.get('send_list_task_week')).do(task_get_jira, mode='every_week')
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1),

    async def on_startup():
        asyncio.create_task(scheduler())

    await on_startup()
    await dp.start_polling(dp)


if __name__ == '__main__':
    asyncio.run(main())

