from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from  DataBase.mongo import MongoRepository
from Schedule.schedule import *
from Teacher.teacher import *
from Group.group import *
from User.user import *
from PushNotifications.Push import *
from threading import Thread
import asyncio
from scheme import DataForPush

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
   return JSONEncoder().encode(await get_teacher_schedule(teacher_id, date))


#создает пользователя или обновляет данные о сущетсвующем
@app.post('/users')
async def add_user_handler(user: User):
    await add_user(user)

#возращает данные о пользователе по его id
@app.get('/users')
async def get_user_handler(user_id: str):
    return await get_user(user_id)

#возврвщает расписание по id пользователя (используется при загрузке приложения)
@app.get('/schedule_by_user_id')
async def get_schedule_by_sub(user_id: str):
    return JSONEncoder().encode(await get_schedule_by_user_id(user_id))


#возвращает данные о пользователи по его инициалам
@app.get('/teacher')
async def get_teacher_handler(teacher_initials): 
    print(1)
    return 1
    return JSONEncoder().encode(await get_teacher(teacher_initials))

#возвращает инициалы преподаватели по его id
@app.get("/teacher_initials")
async def get_teacher_initials_handler(teacher_id):
    return JSONEncoder().encode( await get_teacher(teacher_id))

@app.get("/load_groups")
async def load_groups_handler():
   return JSONEncoder().encode(await load_groups())

@app.get("/load_english_groups")
async def load_english_groups_handler():
    return JSONEncoder().encode(await load_english_groups())
    
@app.get("/group_by_id")
async def group_by_id_handler(group_id):
    return JSONEncoder().encode(await group_by_id(group_id))

@app.get("/group_by_name")
async def group_by_name_handler(name):
    return JSONEncoder().encode(await group_by_name(name))

@app.get("/is_english_group_exist")
async def is_english_group_exist_handler(group_num):
    return JSONEncoder().encode(await is_english_group_exist(group_num))

@app.post("/add_user_to_push_notification")
async  def add_user_to_push_notification_handler(user_push: UserPush):
    return await add_user_to_push(user_push)
    

@app.post("/get_data_for_push")
async def  get_data_for_push_handle(sub: DataForPush):
    return await get_data_for_push(sub.sub)

@app.get("/get_subs_for_push")
async def get_subs_for_push_handler(hour: int):
    return await get_subs_for_push(hour)






    
    
    
        



