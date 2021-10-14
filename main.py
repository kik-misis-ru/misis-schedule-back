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
from  DataBase.mongo import MongoRepository

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
    date_monday =  get_monday(date)
    response = await mongo_repository.get_schedule(group_id, date_monday)
    if response:
        response = await  add_english_schedule(dict(response), english_group_id)
        response["createdAt"] = str(response["createdAt"])
        return JSONEncoder().encode(response)
    else:
        schedule = get_schedule(group_id, date_monday)
        schedule["createdAt"] = str(datetime.utcnow())      
        mongo_repository.create_schedule(schedule)
        schedule_dict = await add_english_schedule(dict(schedule), english_group_id)
        return JSONEncoder().encode(schedule_dict)

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
    response["status"]=statuc_code_not_found
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
    response["status"]=statuc_code_not_found
    return JSONEncoder().encode(response)
    
    
    
        



