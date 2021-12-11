import requests
from datetime import datetime, timedelta
import json
from bson import ObjectId
from scheme import  *


Bells = ["bell_1", "bell_2", "bell_3", "bell_4", "bell_5"]
Days = ["day_1", "day_2", "day_3", "day_4", "day_5", "day_6"]

filial_id = 880


status_code_success = "1"
status_code_not_found = "-1"
status_code_error= "-2"

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# получение json файла с недельным расписанием для группы
def get_schedule_from_api(group_id, date_monday):
    data = {
            'group': group_id,
            'start_date': date_monday
        }
    req = requests.post('https://login.misis.ru/method/schedule.get', data=data)
    if req.status_code !=200:
        response = dict()
        response["status"] = "NOT FOUND"
        return response
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    schedule_json = json.loads(response)
    schedule_dict = dict(schedule_json)
    schedule = check_sub_groups(schedule_dict)
    return schedule

# получение json файла с недельным расписанием для преподавателя
def get_schedule_teacher_from_api(teacher_id, date_monday):
    data = {
            'teacher': teacher_id,
            'start_date':date_monday
        }
    req = requests.post('https://login.misis.ru/method/schedule.get', data=data)
    if req.status_code !=200:
        response = dict()
        response["status"] = "NOT FOUND"
        return response
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    schedule_json = json.loads(response)
    schedule = dict(schedule_json)
    return schedule


#получение json файла с преподавателями
def get_teachers():
    data = {
            'filiation_id': filial_id
        }
    req = requests.post('https://login.misis.ru/method/filiation_info.get', data=data)
    if req.status_code != 200:
        return []
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    filial_info_json = json.loads(response)
    filial_info_dict = dict(filial_info_json)
    teachers_info_response = filial_info_dict['response']
    teachers_info = teachers_info_response['teachers']
    return teachers_info

#получение json файла с группами
def get_groups():
    data = {
            'filiation_id': filial_id
        }
    req = requests.post('https://login.misis.ru/method/filiation_info.get', data=data)
    if req.status_code != 200:
        return []
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    filial_info_json = json.loads(response)
    filial_info_dict = dict(filial_info_json)
    teachers_info_response = filial_info_dict['response']
    teachers_info = teachers_info_response['groups']
    return teachers_info



#выполненяет проверку и исправление ошибок с подгруппами в расписании
def check_sub_groups(schedule_dict):
    if "status" not in schedule_dict or schedule_dict["status"] == "NOT_FOUND" or "schedule" not in schedule_dict:
        return schedule_dict
    subgroups =dict()
    schedule = schedule_dict["schedule"]    
    for bell in Bells:
        if not bell in schedule:
            continue
        schedule_bell = schedule[bell]
        for day in Days:
            if not day in schedule_bell:
                continue
            schedule_day = schedule_bell[day]
            lessons = schedule_day["lessons"]
            if len(lessons)==0:
                continue
            for i in range(len(lessons)):
                lesson = lessons[i]
                subject_id = lesson["subject_id"]
                groups = lesson["groups"]
                if  lesson["type"]=="Лабораторные":
                    for j in range(len(groups)):
                        group=groups[j]
                        subgroup_name = group["subgroup_name"]
                        subGroup = SubGroup(bell, day, subgroup_name, subject_id, i, j)
                        if subject_id in subgroups:
                            if(subgroup_name in subgroups[subject_id]):
                                subgroups[subject_id][subgroup_name].append(subGroup)
                            else:
                                subgroups[subject_id][subgroup_name]=[]
                                subgroups[subject_id][subgroup_name].append(subGroup)

                        else:
                            subgroups[subject_id]=dict()
                            subgroups[subject_id][subgroup_name]=[]
                            subgroups[subject_id][subgroup_name].append(subGroup)

    for key in subgroups:
        if("1" in subgroups[key] and len(subgroups[key]["1"])>0  and ("2" not in subgroups[key] or len(subgroups[key]["2"])==0)):
            for subGroupInf in subgroups[key]["1"]:
                del schedule_dict["schedule"][subGroupInf.bell][subGroupInf.day]["lessons"][subGroup.lesson_num]["groups"][subGroup.group_num]["subgroup_id"]
                del schedule_dict["schedule"][subGroupInf.bell][subGroupInf.day]["lessons"][subGroup.lesson_num]["groups"][subGroup.group_num]["subgroup_name"]
    return schedule_dict

#из стпроки с ФИО получает фамилию и первые буквы имени и отчества
def get_initials_from_str(teacher_initials):

    teacher_initials=teacher_initials.replace('.', ' ')

    while(teacher_initials.__contains__('  ')):
        teacher_initials=teacher_initials.replace('  ', ' ')

    if(teacher_initials.isalpha()):
        return -1
    teacher_initials = teacher_initials.strip()
    initials = teacher_initials.split(' ')

    last_name = initials[0]
    last_name = last_name.capitalize()
    first_name=""
    mid_name=""
    if(len(initials) not in (2,3)):
        return -1

    if(len(initials)==2):
        if(len(initials[1])!=2):
            return -1
        first_and_min_name = initials[1]
        first_name = first_and_min_name[0].upper()
        mid_name = first_and_min_name[1].upper()
    if len(initials)==3:
        first_name = initials[1]
        first_name = first_name.upper()

        mid_name = initials[2]
        mid_name = mid_name.upper()
    return FIO(last_name=last_name,first_name=first_name,mid_name=mid_name)


#приводит строку с ФИО к виду Фамилия И. О.
def formate_teacher_initials(teacher):
     teacher_initials = teacher.split(' ')
     if(len(teacher_initials)==2):
         if(len(teacher_initials[1].strip())==2):
             name_initial = teacher_initials[1][0]
             midname_initial = teacher_initials[1][1]
             return teacher_initials[0]+' '+name_initial+'.'+midname_initial+'.'
     return teacher

#возвращает дату понедельника то недели, к которой относится date
def get_monday(date):
    dateDate = datetime.strptime(date, '%Y-%m-%d').date()
    dateDate -= timedelta(dateDate.isoweekday()-1)
    return dateDate


def find_teahcer(teachers_info, fio):
     response=dict()
     for teacher_info in teachers_info:
            teacher_last_name=teacher_info['last_name']
            teacher_first_name= teacher_info['first_name'][0]
            if teacher_info['mid_name']:
                teacher_mid_name= teacher_info['mid_name'][0]
            if teacher_mid_name is not None:
                if(teacher_last_name==fio.last_name and  teacher_first_name==fio.first_name and teacher_mid_name == fio.mid_name):
                    response = teacher_info
                    response["status"]=status_code_success
                    return response
     response["status"]=status_code_not_found
     return response

def get_user_info(response):
    result = {}
    result["user_id"] = response["user_id"]
    result["filial_id"] = response["filial_id"]
    result["group_id"] = response["group_id"]
    result["subgroup_name"] = response["subgroup_name"]
    result["eng_group"] = response["eng_group"]
    if("teacher_id" in response):
        result["teacher_id"]=response["teacher_id"]
    else:
        result["teacher_id"]=""
    return result

#преобразует расписание, полученное из api к виду,
#в котором оно хранится в базе данных
def formate_schedule(schedule_from_api):
    schedule = dict()
    if "":
        schedule["createdAt"] = datetime.utcnow()
        schedule["start_date"] = schedule_from_api["start_date"]
        schedule["teacher_id"] = schedule_from_api["teacher_id"]
        schedule["group_id"] = schedule_from_api["group_id"]
        schedule["room_id"] = schedule_from_api["room_id"]
        schedule_from_api["schedule_header"] = schedule_from_api["schedule_header"]
        schedule["schedule"] = schedule_from_api["schedule"]
        schedule["prev_date"] = schedule_from_api["prev_date"]
        schedule["next_date"] = schedule_from_api["next_date"]
    return schedule



        


