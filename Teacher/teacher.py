from scheme import *
from utils import *
from English.english import *
from Schedule.schedule import *
from Database.mongo import MongoRepository

mongo_repository = MongoRepository()




async def get_teacher(teacher_initials):
    fio =  get_initials_from_str(teacher_initials)
    response = dict()
    if(fio ==-1):
        response['status']= status_code_error
        return response
    count_rows = await mongo_repository.teachers_count()
    if count_rows == 0:
        teachers_info = get_teachers()
        mongo_repository.fill_teachers(teachers_info)
        response = find_teahcer
        return response
    teacher_from_db = await mongo_repository.find_teacher(fio)
    if teacher_from_db is not None:
        response = teacher_from_db
        response["status"]=status_code_success
        response["createdAt"] = str(response["createdAt"])
        return response
    response["status"]=status_code_not_found

async def get_teacher_initials(teacher_id):
    count_rows = await mongo_repository.teachers_count()
    if count_rows == 0:
        teachers_info = get_teachers()
        mongo_repository.fill_teachers(teachers_info)
        for teacher_info in teachers_info:
            if(teacher_info["Id"]==teacher_id):
                response=teacher_info
                response["status"]="1"
        return response
    teacher_from_db =  await mongo_repository.find_teacher_id(int(teacher_id))
    if teacher_from_db is not None:
        response = teacher_from_db
        response["status"]=status_code_success
        response["createdAt"] = str(response["createdAt"])
        return response
    response = dict()
    response["status"]=status_code_not_found
    return response
