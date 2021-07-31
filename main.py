import pymongo
from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scheme import *


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


client = pymongo.MongoClient('')
db = client.schedule

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('schedule.json', 'r') as f:
    file = f.read()
file = json.loads(file)


@app.post('/schedule')
async def insert_schedule_json():
    _id = db.schedule.insert_one(file).inserted_id
    return str(_id)


@app.get('/schedule')
async def get_schedule_json(group_id):
    response = db.schedule.find_one({"group_id": str(group_id)})
    return JSONEncoder().encode(response)


@app.post('/users')
async def add_user(user: User):
    if db.users.find_one({"user_id": user.user_id}) is None:
        _id = db.users.insert_one(dict(user)).inserted_id
        return str(_id)
    else:
        return "0"
