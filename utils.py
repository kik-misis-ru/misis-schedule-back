import requests
from datetime import datetime, timedelta
import json
from bson import ObjectId
from scheme import  *

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
    req = requests.post('https://login.misis.ru/method/filiation_info.get', data=data)
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    return response


def FillTeachers(collection_schedule_teacher, fio=None, Id=-1):
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