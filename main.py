from datetime import date
from string import printable
from fastapi import FastAPI, Response, responses, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR


from Services.schedule import *
from Services.teacher import *
from Services.group import *
from Services.user import *
from DataBase.mongo import MongoRepository
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

schedule = Schedule(mongo_repository)
user = User(mongo_repository)
teacher = Teacher(mongo_repository)
group = Group(mongo_repository)



#возвращает расписание по дате, id-группы и id-группы по английскому
@app.get('/schedule')
async def get_schedule_json(group_id, english_group_id, date, response: Response):
    result = await schedule.get_schedule(group_id, english_group_id, date)
    if result['status'] == "FOUND":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)

#возврвщает расписание для преподавателя по его id
@app.get("/schedule_teacher")
async  def get_schedule_teacher_json(teacher_id, date, response: Response):
    result = await schedule.get_teacher_schedule(teacher_id, date)
    if result['status'] == "FOUND":
       response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)


#создает пользователя или обновляет данные о сущетсвующем
@app.post('/user')
async def add_user_handler(_user: UserModel, response: Response):
    result = await user.add_user(_user)
    response.status_code = HTTP_201_CREATED


#возращает данные о пользователе по его id
@app.get('/user')
async def get_user_handler(user_id: str, response: Response):
    result = await user.get_user(user_id)
    if result != "0":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return result

#возврвщает расписание по id пользователя (используется при загрузке приложения)
@app.get('/data_by_user_id')
async def get_data_by_sub(user_id: str, response: Response):
    result = await schedule.get_data_by_user_id(user_id)
    if result['status'] == "1":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)


#возвращает данные о пользователи по его инициалам
@app.get('/teacher_by_initials')
async def get_teacher_handler(teacher_initials, response: Response): 
    result = await teacher.get_teacher(teacher_initials)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
    elif result['status'] == '-2':
        response.status_code = HTTP_422_UNPROCESSABLE_ENTITY
    else:
        response.status_code = HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)

#возвращает инициалы преподаватели по его id
@app.get("/teacher_by_id")
async def get_teacher_initials_handler(teacher_id,  response: Response):
    result = await teacher.get_teacher_initials(teacher_id)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
    else:
        response.status_code = HTTP_404_NOT_FOUND
    return  JSONEncoder().encode(result)

#обновляет учебные группы в базе данных (по данным из api)
@app.get("/load_groups")
async def load_groups_handler(response: Response):
   result =  await group.load_groups()
   if result['status'] == '1':
        response.status_code = HTTP_200_OK
   else:
       response.status_code = HTTP_500_INTERNAL_SERVER_ERROR



#обновляет группы по английскому в базе данных (по данным из googleSheets)
@app.get("/load_english_groups")
async def load_english_groups_handler(response: Response):
   result =  await group.load_english_groups()
   if result['status'] == '1':
        response.status_code = HTTP_200_OK
   else:
       response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
    
#получение учебной группы по id
@app.get("/group_by_id")
async def group_by_id_handler(group_id, response: Response):
    result = await group.group_by_id(group_id)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
        return JSONEncoder().encode(result)
    else: 
        response.status_code = HTTP_404_NOT_FOUND
   

#получение учебной группы по е имени
@app.get("/group_by_name")
async def group_by_name_handler(name, response: Response):
    result = await group.group_by_name(name)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
        return JSONEncoder().encode(result)
    else: 
        response.status_code = HTTP_404_NOT_FOUND
    

#проверка сузествования группы по английскому
@app.get("/is_english_group_exist")
async def is_english_group_exist_handler(group_num):
    return JSONEncoder().encode(await group.is_english_group_exist(group_num))

#добавление пуш-нотификаций для пользователя
@app.post("/add_user_to_push_notification")
async  def add_user_to_push_notification_handler(user_push: UserPush, response: Response):
    result = await user.add_user_to_push(user_push)
    if result['status'] == status_code_success:
        response.status_code = HTTP_201_CREATED
    else:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR

    
#получение данных для отправки пуш-нотификаций по sub пользователя
@app.post("/get_data_for_push")
async def  get_data_for_push_handle(sub: DataForPush, response: Response):
    result = await user.get_data_for_push(sub.sub)
    if result['status'] == status_code_success:
        response.status_code = HTTP_200_OK
        return result
    else:
        response.status_code = HTTP_404_NOT_FOUND

     
#получение списка sub-ов пользователей,
#которым надо отправить пуш в переданный час
@app.get("/get_subs_for_push")
async def get_subs_for_push_handler(hour: int):
    return await user.get_subs_for_push(hour)



@app.get('/english_schedule')
async def english_schedule(group_id: str):
    english = English()
    return  english.get_enslish_schedule(group_id)




    
    
    
        



