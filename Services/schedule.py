from scheme import *
from datetime import datetime
from utils import *
from Services.english import *
from DataBase.mongo import MongoRepository




class Schedule:

    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
        self.heroku_time_diff = os.getenv("HEROKU_TIME_DIFF")
        self.english = English()

    async def get_schedule(self, group_id, english_group_id, date):
        date_monday =  get_monday(date)
        response = await self.mongo_repository.get_schedule(group_id, date_monday)
        if not response:
            schedule_from_api = get_schedule_from_api(group_id, date_monday)
            response = formate_schedule(schedule_from_api)
            if "schedule" not in response:
                return {"status": "NOT FOUND"}
            else:
                self.mongo_repository.create_schedule(response)
        response = await  self.english.add_english_schedule(dict(response), english_group_id)
        response["createdAt"] = str(response["createdAt"])
        response["status"] = "FOUND"
        return response

    async def get_teacher_schedule(self, teacher_id, date):
        date_monday =get_monday(date)
        response = await self.mongo_repository.get_schedule_teacher(teacher_id, date_monday)
        if not response:
            schedule_from_api =get_schedule_teacher_from_api(teacher_id, date_monday)
            response = formate_schedule(schedule_from_api)
            if "schedule" not in response:
                return {"status": "NOT FOUND"}
            else:
                self.mongo_repository.create_schedule(response)
        response["createdAt"] = str(response["createdAt"])
        response["status"] = "FOUND"
        return response

    async def get_data_by_user_id(self, user_id: str):
        response = dict()
        user_response = await self.mongo_repository.find_user(user_id)
        if user_response:
            response["status"] = status_code_success
            if user_response["group_id"]!="":
                group = await self.mongo_repository.get_group_by_id(user_response["group_id"])
                response["groupName"] = group["name"]
                response["groupId"] = user_response["group_id"]
            else:
                response["groupName"] = ""
            push_data = await self.mongo_repository.async_get_push_info_user(user_id)
            if push_data:
                response['isActive'] = push_data['isActive']
                response['hour'] = push_data['hour']
                response['minute'] = push_data['minute']
                if "day" in push_data:
                    response['day'] = push_data['day']
                else:
                    response['day'] = 1
            else:
                response['isActive'] = False
                response['hour'] = status_code_not_found
                response['minute'] = status_code_not_found
                response['day'] = 1
            date = datetime.today().strftime('%Y-%m-%d')
            if "teacher_id" in user_response and user_response["teacher_id"] != "":
                teacher_id = user_response["teacher_id"]
                response["teacher_id"] = teacher_id
                response["schedule"] = await self.get_teacher_schedule(teacher_id, date)
                teacher_info= await self.mongo_repository.find_teacher_id(teacher_id)
                response["teacher_info"] = dict()
                response["teacher_info"]["first_name"] = teacher_info["first_name"]
                response["teacher_info"]["last_name"] = teacher_info["last_name"]
                response["teacher_info"]["mid_name"] = teacher_info["mid_name"]
            else:
                group_id = user_response["group_id"]
                english_group_id = user_response["eng_group"]
                schedule =  await self.get_schedule(group_id, english_group_id, date)
                response["schedule"] = schedule
        else:
            response["status"] = status_code_not_found
        return response