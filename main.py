import pymongo
from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scheme import *
import requests


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


client = pymongo.MongoClient('mongodb+srv://user615:passforuser615@cluster0.xtaai.mongodb.net/'
                             'myFirstDatabase?retryWrites=true&w=majority')
db = client.schedule

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('schedule_test.json', 'r', encoding='utf-8') as f:
    file = f.read()
file = json.loads(file)

filial_id = "808"
group_id = "6156"
room_id = None
teacher_id = None
start_date = '2021-05-10'

# получение json файла с недельным расписанием для группы
def get_json(data):
    req = requests.post('https://login.misis.ru/method/schedule.get', data=data)
    response = json.dumps(req.json(), indent=2, ensure_ascii=False)
    return response


@app.post('/schedule')
async def insert_schedule_json(schedule):
    _id = db.schedule.insert_one(schedule).inserted_id
    return str(_id)


@app.get('/schedule')
async def get_schedule_json(group_id, date):
    response = db.schedule.find_one({"group_id": str(group_id), "start_date": str(date)})
    if response:
        return JSONEncoder().encode(response)
    else:
        data = {
            'group': group_id,
            'start_date': date
        }
        return get_json(data)


@app.post('/users')
async def add_user(user: User):
    if db.users.find_one({"user_id": user.user_id}) is None:
        _id = db.users.insert_one(dict(user)).inserted_id
        return str(_id)
    else:
        return "0"

@app.get('/users')
async def get_user(user_id: str):
    if db.users.find_one({"user_id": user_id}):
        response = db.users.find_one({"user_id": user_id})
        result = {}
        result["user_id"] = response["user_id"]
        result["filial_id"] = response["filial_id"]
        result["group_id"] = response["group_id"]
        result["subgroup_name"] = response["subgroup_name"]
        result["eng_group"] = response["eng_group"]
        return result
    else:
        return "0"
