import requests
from bs4 import BeautifulSoup
import json

URL = 'https://edu.misis.ru/schedule/moscow/current'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/91.0.4472.135 Mobile Safari/537.36',
    'accept': '*/*'}


# получение html кода страницы
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


# парсинг html и запись в файл
def parse():
    html = get_html(URL)
    if html.status_code == 200:
        pass
        # src = html.text
        # with open('index.html', 'w', encoding="utf-8") as file:
        #     file.write(src)
    else:
        print('Error')


# получение информации о филиале, группах, кабинетах и учителях
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    # поиск расписания в html коде
    sсhedule = soup.find("schedule")

    # формирование словарей из атрибутов JSON
    filial_data = json.loads(sсhedule.attrs[':filial'])
    groups_data = json.loads(sсhedule.attrs[':groups'])
    rooms_data = json.loads(sсhedule.attrs[':rooms'])
    teachers_data = json.loads(sсhedule.attrs[':teachers'])
    return [filial_data, groups_data, rooms_data, teachers_data]


# определение id группы по ее названию
def get_group_id(group_name):
    for group in groups_data:
        if group['name'].upper() == group_name.upper():
            return group["id"]


# получение json файла с недельным расписанием для группы
def get_json(data):
    req = requests.post('https://login.misis.ru/method/schedule.get', data=data)
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    return response


# помещение расписания в файл schedule.json
def put_schedule_in_file():
    with open('schedule.json', 'w', encoding='utf-8') as file:
        file.write(schedule_json)


# чтение содержимого из файла index.html
with open('index.html', 'r', encoding="utf-8") as file:
    src = file.read()

attrs_list = get_content(src)

filial_data = attrs_list[0]
groups_data = attrs_list[1]
rooms_data = attrs_list[2]
teachers_data = attrs_list[3]

filial_id = filial_data['id']
group_id = get_group_id('БПМ-19-2')
room_id = None
teacher_id = None
start_date = '2021-05-10'

# формирование данных для запроса через API
data = {
    'filial': filial_id,
    'group': group_id,
    'room': room_id,
    'teacher': teacher_id,
    'start_date': start_date
}

#schedule_json = get_json(data) 

# чтение содержимого из файла schedule.json
with open('schedule.json', 'r', encoding='utf-8') as file:
    schedule_json = file.read()

# преобразовние json в словарь
schedule_dict = json.loads(schedule_json)

# получение расписания на каждый день
for day_num in range(1, 7):
    for bell in schedule_dict['schedule']:
        if schedule_dict['schedule'][bell][f'day_{day_num}']['lessons']:
            print(schedule_dict['schedule'][bell][f'day_{day_num}']['lessons'][0]['subject_name'])
    print()



