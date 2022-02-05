from datetime import date
from urllib import response
from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from Services.schedule import *
from Services.teacher import *
from Services.group import *
from Services.user import *
from DataBase.mongo import MongoRepository
from Auth.auth import Token, ACCESS_TOKEN_EXPIRE_MINUTES, Auth
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
auth = Auth(mongo_repository)


#возвращает расписание по дате, id-группы и id-группы по английскому
@app.get('/schedule')
async def get_schedule_json(group_id, english_group_id, date, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await schedule.get_schedule(group_id, english_group_id, date)
    if result['status'] == "FOUND":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)

#возврвщает расписание для преподавателя по его id
@app.get("/schedule_teacher")
async  def get_schedule_teacher_json(teacher_id, date, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await schedule.get_teacher_schedule(teacher_id, date)
    if result['status'] == "FOUND":
       response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)


#создает пользователя или обновляет данные о сущетсвующем
@app.post('/user')
async def add_user_handler(_user: UserModel, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await user.add_user(_user)
    response.status_code = HTTP_201_CREATED


#возращает данные о пользователе по его id
@app.get('/user')
async def get_user_handler(user_id: str, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await user.get_user(user_id)
    if result != "0":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return result

#возврвщает расписание по id пользователя (используется при загрузке приложения)
@app.get('/data_by_user_id')
async def get_data_by_sub(user_id: str, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await schedule.get_data_by_user_id(user_id)
    if result['status'] == "1":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
    return JSONEncoder().encode(result)


#возвращает данные о пользователи по его инициалам
@app.get('/teacher_by_initials')
async def get_teacher_handler(teacher_initials, response: Response,  _: User = Depends(auth.get_current_user)): 
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
async def get_teacher_initials_handler(teacher_id,  response: Response,  _: User = Depends(auth.get_current_user)):
    result = await teacher.get_teacher_initials(teacher_id)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
    else:
        response.status_code = HTTP_404_NOT_FOUND
    return  JSONEncoder().encode(result)

#обновляет учебные группы в базе данных (по данным из api)
@app.get("/load_groups")
async def load_groups_handler(response: Response,  _: User = Depends(auth.get_current_user)):
   result =  await group.load_groups()
   if result['status'] == '1':
        response.status_code = HTTP_200_OK
   else:
       response.status_code = HTTP_500_INTERNAL_SERVER_ERROR



#обновляет группы по английскому в базе данных (по данным из googleSheets)
@app.get("/load_english_groups")
async def load_english_groups_handler(response: Response,  _: User = Depends(auth.get_current_user)):
   result =  await group.load_english_groups()
   if result['status'] == '1':
        response.status_code = HTTP_200_OK
   else:
       response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
    
#получение учебной группы по id
@app.get("/group_by_id")
async def group_by_id_handler(group_id, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await group.group_by_id(group_id)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
        return JSONEncoder().encode(result)
    else: 
        response.status_code = HTTP_404_NOT_FOUND
   

#получение учебной группы по е имени
@app.get("/group_by_name")
async def group_by_name_handler(name, response: Response,  _: User = Depends(auth.get_current_user)):
    result = await group.group_by_name(name)
    if result['status'] == '1':
        response.status_code = HTTP_200_OK
        return JSONEncoder().encode(result)
    else: 
        response.status_code = HTTP_404_NOT_FOUND
    

#проверка сузествования группы по английскому
@app.get("/is_english_group_exist")
async def is_english_group_exist_handler(group_num, _: User = Depends(auth.get_current_user)):
    return JSONEncoder().encode(await group.is_english_group_exist(group_num))

#добавление пуш-нотификаций для пользователя
@app.post("/add_user_to_push_notification")
async  def add_user_to_push_notification_handler(user_push: UserPush, response: Response, _: User = Depends(auth.get_current_user)):
    result = await user.add_user_to_push(user_push)
    if result['status'] == status_code_success:
        response.status_code = HTTP_201_CREATED
    else:
        response.status_code = HTTP_500_INTERNAL_SERVER_ERROR

    
#получение данных для отправки пуш-нотификаций по sub пользователя
@app.post("/get_data_for_push")
async def  get_data_for_push_handle(sub: DataForPush, response: Response, _: User = Depends(auth.get_current_user)):
    result = await user.get_data_for_push(sub.sub)
    if result['status'] == status_code_success:
        response.status_code = HTTP_200_OK
        return result
    else:
        response.status_code = HTTP_404_NOT_FOUND


     
#получение списка sub-ов пользователей,
#которым надо отправить пуш в переданный час
@app.get("/get_subs_for_push")
async def get_subs_for_push_handler(hour: int, _: User = Depends(auth.get_current_user)):
    return await user.get_subs_for_push(hour)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/english_schedule')
async def english_schedule(group_id: str):
    english = English()
    return  english.get_enslish_schedule(group_id)




    
    
    
        



