import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from bot import dp
from handler import handler
from sheduler_tasks import task_check_backup_local, task_check_backup_ya_disk, task_get_jira


async def main():
    try:
        await handler()

        async def get_day():
            day_of_month = datetime.datetime.now().day
            if day_of_month == 11:
                await task_get_jira('every_month')

        async def scheduler():
            scheduler_back_local = AsyncIOScheduler()
            scheduler_back_local.add_job(task_check_backup_local, trigger=config.tr_backup)
            scheduler_back_local.start()
            scheduler_back_ya = AsyncIOScheduler()
            scheduler_back_ya.add_job(task_check_backup_ya_disk, trigger=config.tr_backup)
            scheduler_back_ya.start()

        async def on_startup():
            asyncio.create_task(scheduler())

        await on_startup()
        await dp.start_polling(dp)

    except Exception as ex:
        print()


if __name__ == '__main__':
    asyncio.run(main())
