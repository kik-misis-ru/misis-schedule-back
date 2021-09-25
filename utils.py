import requests
from datetime import datetime, timedelta
import json
from bson import ObjectId
from scheme import  *


Bells = ["bell_1", "bell_2", "bell_3", "bell_4", "bell_5"]
Days = ["day_1", "day_2", "day_3", "day_4", "day_5", "day_6"]
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

# получение json файла с недельным расписанием для группы
def get_json(data):
    req = requests.post('https://login.misis.ru/method/schedule.get', data=data)
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    return response

#получение json файла с преподавателями
def get_json_teachers(data):
    print(data)
    req = requests.post('https://login.misis.ru/method/filiation_info.get', data=data)
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    return response


def fill_teachers(collection_schedule_teacher, fio=None, Id=-1):
    data = {
            'filiation_id': 880
        }
    filial_info = get_json_teachers(data)
    filial_info_json = json.loads(filial_info)
    filial_info_dict = dict(filial_info_json)
    teachers_info = filial_info_dict['response']['teachers']
    createdAt = datetime.utcnow()
    response = dict()
    response['status']="-1"
    for teacher_info in teachers_info:
        teacher_info['createdAt'] = createdAt
        teacher_info['first_name']= teacher_info['first_name'][0]
        if teacher_info['mid_name'] is not None:
            teacher_info['mid_name']= teacher_info['mid_name'][0]
            if(fio is not None):
                if(teacher_info['last_name']==fio.last_name and  teacher_info['first_name']==fio.first_name and teacher_info['mid_name']== fio.mid_name):
                    response = teacher_info
                    response["status"]="1"
            elif Id is not None:
                if(teacher_info["Id"]==Id):
                    response=teacher_info
                    response["status"]="1"
    collection_schedule_teacher.insert_many(teachers_info)
    return response

def check_sub_groups(schedule_dict):
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
            if len(schedule_day["lessons"])==0:
                continue
            for i in range(len(schedule_day["lessons"])):
                lesson = schedule_day["lessons"][i]
                if  lesson["type"]=="Лабораторные":
                    for j in range(len(lesson["groups"])):
                        group=lesson["groups"][j]
                        subGroup = SubGroup(bell, day, group["subgroup_name"] ,lesson["subject_id"], i, j)
                        if lesson["subject_id"] in subgroups:
                            if(group["subgroup_name"] in subgroups[lesson["subject_id"]]):
                                subgroups[lesson["subject_id"]][group["subgroup_name"]].append(subGroup)
                            else:
                                subgroups[lesson["subject_id"]][group["subgroup_name"]]=[]
                                subgroups[lesson["subject_id"]][group["subgroup_name"]].append(subGroup)

                        else:
                            subgroups[lesson["subject_id"]]=dict()
                            subgroups[lesson["subject_id"]][group["subgroup_name"]]=[]
                            subgroups[lesson["subject_id"]][group["subgroup_name"]].append(subGroup)

    for key in subgroups:
        if("1" in subgroups[key] and len(subgroups[key]["1"])>0  and ("2" not in subgroups[key] or len(subgroups[key]["2"])==0)):
            for subGroupInf in subgroups[key]["1"]:
                print(subGroupInf)
                del schedule_dict["schedule"][subGroupInf.bell][subGroupInf.day]["lessons"][subGroup.lesson_num]["groups"][subGroup.group_num]["subgroup_id"]
                del schedule_dict["schedule"][subGroupInf.bell][subGroupInf.day]["lessons"][subGroup.lesson_num]["groups"][subGroup.group_num]["subgroup_name"]
    return schedule_dict

def get_initials_from_str(teacher_initials):
    teacher_initials=teacher_initials.replace('.', ' ')
    
    while(teacher_initials.__contains__('  ')):
        teacher_initials=teacher_initials.replace('  ', ' ')
    if(teacher_initials.isalpha()):
        return -1
    teacher_initials = teacher_initials.strip()
    initials = teacher_initials.split(' ')
    if(len(initials)==2):
        if(len(initials[1])!=2):
            return -1
        last_name = initials[0].capitalize()
        first_name = initials[1][0].upper()
        mid_name = initials[1][1].upper()
        print([last_name, first_name , mid_name])
        return [last_name, first_name , mid_name]
    if len(initials)==3:
        last_name = initials[0].capitalize()
        first_name = initials[1].upper()
        mid_name = initials[2].upper()
        print([last_name, first_name , mid_name])
        return [last_name, first_name , mid_name]
    return -1
    
        


