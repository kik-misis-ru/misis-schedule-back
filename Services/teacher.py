from scheme import *
from utils import *
from Services.english import *
from Services.schedule import *
# from DataBase.mongo import MongoRepository

class Teacher:

    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
    async def get_teacher(self, teacher_initials):
        fio =  get_initials_from_str(teacher_initials)
        response = dict()
        if(fio ==-1):
            response['status']= status_code_error
            return response
        count_rows = await self.mongo_repository.teachers_count()
        if count_rows == 0:
            teachers_info = get_teachers()
            self.mongo_repository.fill_teachers(teachers_info)
            response = find_teahcer
            return response
        teacher_from_db = await self.mongo_repository.find_teacher(fio)
        if teacher_from_db is not None:
            response = teacher_from_db
            response["status"]=status_code_success
            response["createdAt"] = str(response["createdAt"])
            return response
        response["status"]=status_code_not_found
        return response

    async def get_teacher_initials(self, teacher_id):
        count_rows = await self.mongo_repository.teachers_count()
        if count_rows == 0:
            teachers_info = get_teachers()
            self.mongo_repository.fill_teachers(teachers_info)
            for teacher_info in teachers_info:
                if(teacher_info["Id"]==teacher_id):
                    response=teacher_info
                    response["status"]="1"
            return response
        teacher_from_db =  await self.mongo_repository.find_teacher_id(int(teacher_id))
        if teacher_from_db is not None:
            response = teacher_from_db
            response["status"]=status_code_success
            response["createdAt"] = str(response["createdAt"])
            return response
        response = dict()
        response["status"]=status_code_not_found
        return response
