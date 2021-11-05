from requests.models import Response, requote_uri
from pydantic.networks import import_email_validator
from english import get_enslish_schedule
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scheme import *
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
from utils import *
from english import *
from  Database.mongo import MongoRepository
from Schedule.schedule import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_repository = MongoRepository()

#возвращает расписание по дате, id-группы и id-группы по английскому
@app.get('/schedule')
async def get_schedule_json(group_id, english_group_id, date):
    return JSONEncoder().encode(await get_schedule(group_id, english_group_id, date))

#возврвщает расписание для преподавателя по его id
@app.get("/schedule_teacher")
async  def get_schedule_teacher_json(teacher_id, date):
    date_monday =get_monday(date)
    response = await mongo_repository.get_schedule_teacher(teacher_id, date_monday)
    if response:
        response["createdAt"] = str(response["createdAt"])
        return JSONEncoder().encode(response)
    else:
        schedule =get_schedule_teacher(teacher_id, date_monday)
        schedule["createdAt"] = str(datetime.utcnow())
        mongo_repository.create_teacher_schedule(schedule)
        return JSONEncoder().encode(schedule)


#создает пользователя или обновляет данные о сущетсвующем
@app.post('/users')
async def add_user(user: User):
    if await mongo_repository.find_user(user.user_id) is None:
        mongo_repository.create_user(dict(user))
    else:
        mongo_repository.update_user(user)

#возращает данные о пользователе по его id
@app.get('/users')
async def get_user(user_id: str):
    response = await mongo_repository.find_user(user_id)
    if response:
        result = get_user_info(response)
        return result
    else:
        return "0"

@app.get('/schedule_by_user_id')
async def get_schedule_by_sub(user_id: str):
    start = datetime.now()
    response = await mongo_repository.find_user(user_id)
    print(datetime.now()-start)
    group = await mongo_repository.get_group_by_id(response["group_id"])
    response["groupName"] = group["name"]
    date = datetime.today().strftime('%Y-%m-%d')
    if "teacher_id" in response and response["teacher_id"] != "":
        response["schedule"] = await get_schedule_teacher_json(response["teacher_id"], date)
        response["teacherInfo"] = await mongo_repository.find_teacher_id(response["teacher_id"])
    else:
        group_id = response["group_id"]
        english_group_id = response["eng_group"]
        schedule =  await get_schedule(group_id, english_group_id, date)
        response["schedule"] = schedule
    print(datetime.now() - start)
    return JSONEncoder().encode(response)




#возвращает данные о пользователи по его инициалам
@app.get('/teacher')
async def get_teacher(teacher_initials): 
    fio =  get_initials_from_str(teacher_initials)
    response = dict()
    if(fio ==-1):
        response['status']= status_code_error
        return JSONEncoder().encode(response)
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
        return JSONEncoder().encode(response)
    response["status"]=status_code_not_found
    return JSONEncoder().encode(response)

#возвращает инициалы преподаватели по его id
@app.get("/teacher_initials")
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
        return JSONEncoder().encode(response)
    response = dict()
    response["status"]=status_code_not_found
    return JSONEncoder().encode(response)

@app.get("/load_groups")
async def load_groups():
    response = dict()
    delete_result = await mongo_repository.delete_grouplist()
    if(delete_result.deleted_count==0):
        count_rows = await mongo_repository.collection_group_list()
        if(count_rows!=0):
            response["status"] = status_code_error
            return response
    groups = get_groups()
    insert_result = await mongo_repository.create_grouplist(groups)
    
    if(len(insert_result.inserted_ids)>0):
        response["status"] = status_code_success
    else:
        response["status"] = status_code_error
    return response

@app.get("/load_english_groups")
async def load_english_groups():
    response = dict()
    delete_result = await mongo_repository.delete_english_group_list()
    if(delete_result.deleted_count==0):
        count_rows = await mongo_repository.count_engslish_group_list()
        if(count_rows!=0):
            response["status"] = status_code_error
            return response
    groups = get_all_english_groups()
    insert_result = await mongo_repository.create_english_groups(groups)
    if(len(insert_result.inserted_ids)>0):
        response["status"] = status_code_success
    else:
        response["status"] = status_code_error
    return response
    
@app.get("/group_by_id")
async def group_by_id(group_id):
    response = dict()
    group = await mongo_repository.get_group_by_id(group_id)
    if group:
         response['id'] = group['id']
         response['name'] = group['name']
         response["status"]= status_code_success
         return response
    else:
        response["status"] = status_code_not_found
        return response

@app.get("/group_by_name")
async def group_by_name(name):
    response = dict()
    group = await mongo_repository.get_group_by_name(name)
    if group:
         response['id'] = group['id']
         response['name'] = group['name']
         response["status"]= status_code_success
         return response
    else:
        response = dict()
        response["status"] = status_code_not_found
        return response

@app.get("/is_english_group_exist")
async def is_english_group_exist(group_num):
    group = await mongo_repository.find_english_group(group_num)
    response = dict()
    if(group):
        response["status"] = status_code_success
    else:
        response["status"] = status_code_not_found
    return response


    
    
    
        



