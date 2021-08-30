from datetime import date

from requests.sessions import should_bypass_proxies
from pydantic.types import Json
import pymongo
from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scheme import *
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

url = os.getenv("MONGO_CONNECTION_STRING")
print(url)
client = AsyncIOMotorClient(url)

db = client.get_database("schedule")
collection_schedule = db.get_collection("schedule")
collection_users = db.get_collection("users")
#collection_schedule.create_index("createdAt", expireAfterSeconds= 86400)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# получение json файла с недельным расписанием для группы
def get_json(data):
    req = requests.post('https://login.misis.ru/method/schedule.get', data=data)
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    return response


@app.get('/schedule')
async def get_schedule_json(group_id, date):
    in_db_start_time = time.time()
    print('1')
    response = await collection_schedule.find_one({"group_id": str(group_id), "start_date": str(date)})
    print('2')
    if response:
        print("in db")
        in_db_end_time = time.time()
        print("IN DB", in_db_end_time - in_db_start_time)
        response["createdAt"] = str(response["createdAt"])
        return JSONEncoder().encode(response)
    else:
        not_in_db_start_time = time.time()
        print("not in db")
        data = {
            'group': group_id,
            'start_date': date
        }
        print('3')
        sch = get_json(data)
        #print(sch)
        print('4')
        schedule_json = json.loads(sch)
        schedule_dict = dict(schedule_json)
        schedule_dict["createdAt"] = datetime.utcnow()
        collection_schedule.insert_one(schedule_dict)
        print('5')
        not_in_db_end_time = time.time()
        print("NOT IN DB", not_in_db_end_time - not_in_db_start_time)
        return JSONEncoder().encode(schedule_json)



@app.post('/users')
async def add_user(user: User):
    if await collection_users.find_one({"user_id": user.user_id}) is None:
        await collection_test.insert_one(dict(user))
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

