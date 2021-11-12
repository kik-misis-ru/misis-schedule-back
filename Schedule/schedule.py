from scheme import *
from datetime import datetime
from utils import *
from English.english import *
from DataBase.mongo import MongoRepository

mongo_repository = MongoRepository()


async def get_schedule(group_id, english_group_id, date):
    date_monday =  get_monday(date)
    response = await mongo_repository.get_schedule(group_id, date_monday)
    
    if response:
        response = await  add_english_schedule(dict(response), english_group_id)
        response["createdAt"] = str(response["createdAt"])
        return response
    else:
        schedule = get_schedule_from_api(group_id, date_monday)
        schedule["createdAt"] = str(datetime.utcnow())      
        mongo_repository.create_schedule(schedule)
        schedule_dict = await add_english_schedule(dict(schedule), english_group_id)
        return schedule_dict

async def get_teacher_schedule(teacher_id, date):
    date_monday =get_monday(date)
    response = await mongo_repository.get_schedule_teacher(teacher_id, date_monday)
    if response:
        response["createdAt"] = str(response["createdAt"])
        return response
    else:
        schedule =get_schedule_teacher_from_api(teacher_id, date_monday)
        schedule["createdAt"] = str(datetime.utcnow())
        mongo_repository.create_teacher_schedule(schedule)
        return schedule
async def get_schedule_by_user_id(user_id: str):
    response = await mongo_repository.find_user(user_id)
    group = await mongo_repository.get_group_by_id(response["group_id"])
    response["groupName"] = group["name"]
    date = datetime.today().strftime('%Y-%m-%d')
    if "teacher_id" in response and response["teacher_id"] != "":
        teacher_id = response["teacher_id"]
        response["schedule"] = await get_teacher_schedule(teacher_id, date)
        teacher_info= await mongo_repository.find_teacher_id(teacher_id)
        response["teacher_info"] = dict()
        response["teacher_info"]["first_name"] = teacher_info["first_name"]
        response["teacher_info"]["last_name"] = teacher_info["last_name"]
        response["teacher_info"]["mid_name"] = teacher_info["mid_name"]
    else:
        group_id = response["group_id"]
        english_group_id = response["eng_group"]
        schedule =  await get_schedule(group_id, english_group_id, date)
        response["schedule"] = schedule
    return response