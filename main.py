from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scheme import *
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
from utils import *



load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

url = os.getenv("MONGO_CONNECTION_STRING")
print(url)
client = AsyncIOMotorClient(url)

db = client.get_database("schedule")
collection_schedule = db.get_collection("schedule")
collection_schedule_teacher = db.get_collection("schedule_teacher")
collection_users = db.get_collection("users")
collection_teachers = db.get_collection("teachers")





app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get('/schedule')
async def get_schedule_json(group_id, dateStr):
    date = datetime.strptime(dateStr, '%Y-%m-%d').date()
    date -= timedelta(date.isoweekday()-1)
    response = await collection_schedule.find_one({"group_id": str(group_id), "start_date": str(date)})
    if response:
        response["createdAt"] = str(response["createdAt"])
        return JSONEncoder().encode(response)
    else:
        data = {
            'group': group_id,
            'start_date': date
        }
        sch = get_json(data)
        schedule_json = json.loads(sch)
        schedule_dict = dict(schedule_json)
        schedule_dict["createdAt"] = datetime.utcnow()
        collection_schedule.insert_one(schedule_dict)
        return JSONEncoder().encode(schedule_json)

@app.get("/schedule_teacher")
async  def get_schedule_teacher_json(teacher_id, dateStr):
    date = datetime.strptime(dateStr, '%Y-%m-%d').date()
    date -= timedelta(date.isoweekday()-1)
    response = await collection_schedule_teacher.find_one({"teacher_id": str(teacher_id), "start_date":str(date)})
    if response:
        response["createdAt"] = str(response["createdAt"])
        return JSONEncoder().encode(response)
    else:
        data = {
            'teacher': teacher_id,
            'start_date':date
        }
        sch = get_json(data)
        print(1)
        schedule_json = json.loads(sch)
        schedule_dict = dict(schedule_json)
        schedule_dict["createdAt"] = datetime.utcnow()
        collection_schedule_teacher.insert_one(schedule_dict)
        return JSONEncoder().encode(schedule_json)



@app.post('/users')
async def add_user(user: User):
    if await collection_users.find_one({"user_id": user.user_id}) is None:
        await collection_users.insert_one(dict(user))
    else:
        collection_users.update_one({"user_id": user.user_id},
                                    {"$set":
                                         {"filial_id": user.filial_id,
                                          "group_id": user.group_id,
                                          "subgroup_name": user.subgroup_name,
                                          "eng_group": user.eng_group}
                                     })


@app.get('/users')
async def get_user(user_id: str):
    if await collection_users.find_one({"user_id": user_id}):
        response = await collection_users.find_one({"user_id": user_id})
        result = {}
        result["user_id"] = response["user_id"]
        result["filial_id"] = response["filial_id"]
        result["group_id"] = response["group_id"]
        result["subgroup_name"] = response["subgroup_name"]
        result["eng_group"] = response["eng_group"]
        return result
    else:
        return "0"


@app.get('/teacher')
async def get_teacher(teacher_initials):  
    arr_initials = teacher_initials.split(' ')
    if(len(arr_initials)!=3):
        return "-1"
    if(not arr_initials[1].endswith('.') or not arr_initials[2].endswith('.') or len(arr_initials[1])!=2 or len(arr_initials[2])!=2):
        return "-1"
    last_name = arr_initials[0]
    first_name = arr_initials[1][0]
    mid_name = arr_initials[2][0]
    teachers_db = await collection_teachers.find_one()
    if teachers_db is None:
        fio = FIO(last_name=last_name,first_name=first_name,mid_name=mid_name)
        response = FillTeachers(collection_teachers, fio)
        return response
    if await collection_teachers.find_one({'last_name': last_name, 'first_name': first_name, 'mid_name':mid_name}):
        response = await collection_teachers.find_one({'last_name': last_name, 'first_name': first_name, 'mid_name':mid_name})
        response["createdAt"] = str(response["createdAt"])
        return JSONEncoder().encode(response)
    return "-1"
    
        



