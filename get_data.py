import calendar
import datetime
import json

import aiohttp
import yadisk
from atlassian import Jira

from config import auth_ya_disk, jira_conf, auth_ya_disk_two_acc
from ip_list import list_folder_in_yadisk


async def check_backup_local(sheduler=False):
    y = yadisk.YaDisk(token=auth_ya_disk.split(' ')[1])
    y.download('/БЭКАПЫ/listLocalBackup.json', 'listLocalBackup.json')
    with open('listLocalBackup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data.get('day') != str(datetime.datetime.now().date()):
        return {'error': '❌❌❌ Не получен актуальный файл с данными ❌❌❌\n'}
    data.pop('day', None)
    str_prettify = '    Бэкапы локальные \n'
    for i in data:
        if data.get(i) != 1:
            str_prettify = str_prettify + f'❌ {i}: {data.get(i)} \n'
        else:
            str_prettify = str_prettify + f'✅ {i}: {data.get(i)} \n'

    if sheduler:
        return data
    else:
        return str_prettify


async def check_backup_yadisk(sheduler=False):
    data = {}
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')
    for i in list_folder_in_yadisk:
        try:
            headers = {
                'Accept': 'application/json',
                'Authorization': auth_ya_disk_two_acc if i == 'newbase' else auth_ya_disk,
            }
            params = (
                ('path', list_folder_in_yadisk.get(i)),
                ('preview_crop', 'false'),
                ('limit', '150'),
            )
            async with aiohttp.ClientSession() as Session:
                async with Session.get('https://cloud-api.yandex.net/v1/disk/resources', headers=headers,
                                       params=params) as resp:
                    response = await resp.json()
            # if i == 'newbase':
            #     asd = 2
            if len(response.get('_embedded').get('items')) == 0:
                data[i] = 'Папка пуста'
            else:
                for file in response.get('_embedded').get('items'):
                    if file.get('name').split('_')[-1].split('.')[0] == date_now:
                        data[i] = 1
                        break
                    else:
                        data[i] = 0
        except Exception as ex:
            data[i] = ex

    str_prettify = '    Бэкапы с ya диска \n'
    for i in data:
        if data.get(i) != 1:
            str_prettify = str_prettify + f'❌ {i}: {data.get(i)} \n'
        else:
            str_prettify = str_prettify + f'✅ {i}: {data.get(i)} \n'
    if sheduler:
        return data
    else:
        return str_prettify


async def get_jira_task(mode=''):
    jira = Jira(
        url=jira_conf['jira_url'],
        username=jira_conf['jira_username'],
        password=jira_conf['jira_token']
    )
    jql_request = ''
    if mode == 'every_week':
        jql_request = 'project = IT AND status = Выполнено AND resolved >= -5d ORDER BY created DESC'
    elif mode == 'every_month':
        past_month = datetime.datetime.now().month - 1
        year = datetime.datetime.now().year
        last_day_month = calendar.monthrange(year, past_month)

        jql_request = f'resolved >= {year}-{past_month}-01 AND resolved <= {year}-{past_month}-{last_day_month[1]} ' \
                      f'AND status = Выполнено ORDER BY created DESC'

    issues = jira.jql(jql_request, limit=500)
    data = {}
    data_err = ''
    for i in issues.get('issues'):
        try:
            if data.get(i.get('fields').get('assignee').get('displayName')) is None:
                data[i.get('fields').get('assignee').get('displayName')] = [f"{i.get('fields').get('summary')} - "
                                                                            f"{i.get('fields').get('timetracking').get('timeSpent')}"]
            else:
                data[i.get('fields').get('assignee').get('displayName')].append(f"{i.get('fields').get('summary')} - "
                                                                                f"{i.get('fields').get('timetracking').get('timeSpent')}")
        except Exception as ex:
            data_err = data_err + i.get('key') + ' '

    if mode == 'every_month':
        str_prettify = f"📊  <b>Выполненные работы за прошедший месяц:</b> \n\n"
    else:
        str_prettify = f"📊  <b>Выполненные работы за последние 5 дней:</b> \n\n"
    for employee in data:
        str_prettify = str_prettify + f"        🚹<b>{employee}:</b> \n\n"
        for task_time in data.get(employee):
            str_prettify = str_prettify + f'❇️{task_time} \n'
        str_prettify = str_prettify + '\n\n'
    if len(data_err) > 0:
        str_prettify = str_prettify + f'❌ <b>Ошибка. Не установлены исполнители в задачах</b>: {data_err}'

    return str_prettify
