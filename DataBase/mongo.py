from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime
import motor
from motor.motor_asyncio import AsyncIOMotorClient
from scheme import  UserPush



class MongoRepository:
    def __init__(self):
       
        load_dotenv()
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        url = os.getenv("MONGO_CONNECTION_STRING")
        client =  AsyncIOMotorClient(url)
        db = client.get_database("schedule")
        self.collection_schedule = db.get_collection("schedule")
        self.collection_schedule_teacher = db.get_collection("schedule_teacher")
        self.collection_users = db.get_collection("users")
        self.collection_teachers = db.get_collection("teachers")
        self.collection_group_list = db.get_collection("group_list")
        self.collection_english_group_list = db.get_collection("english_group_list")
        self.collection_users_with_push = db.get_collection("users_with_push")

    async def get_schedule(self, group_id, date_monday):
        print("groud_id", group_id)
        print("datw_monday", date_monday)
        return await self.collection_schedule.find_one({"group_id": str(group_id), "start_date": str(date_monday)})
    
    def create_schedule(self, schedule):
        self.collection_schedule.insert_one(schedule)

    async def get_schedule_teacher(self, teacher_id, date_monday):
        return await self.collection_schedule_teacher.find_one({"teacher_id": str(teacher_id), "start_date":str(date_monday)})
    
    def create_teacher_schedule(self, schedule):
        self.collection_schedule_teacher.insert_one(schedule)

    async def find_user(self, user_id):
        return await self.collection_users.find_one({"user_id": user_id})

    async def create_user(self, user):
        return await self.collection_users.insert_one(user)
    
    async def update_user(self, user):
        if(user.group_id == "undefined"):
            return
        return await self.collection_users.update_one({"user_id": user.user_id},
                                    {"$set":
                                         {"filial_id": user.filial_id,
                                          "group_id": user.group_id,
                                          "subgroup_name": user.subgroup_name,
                                          "eng_group": user.eng_group,
                                          "teacher_id":user.teacher_id}

                                     })
    async def teachers_count(self):
        return await self.collection_teachers.estimated_document_count()

    def fill_teachers(self, teachers_info):
        createdAt = datetime.utcnow()
        for teacher_info in teachers_info:
            teacher_info['createdAt'] = createdAt
            teacher_info['first_name']= teacher_info['first_name'][0]
            if teacher_info['mid_name']:
                teacher_info['mid_name']= teacher_info['mid_name'][0]
        self.collection_schedule_teacher.insert_many(teachers_info)

    async def find_teacher(self, fio):
        #await self.collection_schedule.create_index("createdAt", expireAfterSeconds= 30)
        return await self.collection_teachers.find_one({'last_name': fio.last_name, 'first_name': fio.first_name, 'mid_name':fio.mid_name})
    
    async def find_teacher_id(self, teacher_id):
        return await self.collection_teachers.find_one({'id':int(teacher_id)})

    async def create_grouplist(self, group_list):
        print(group_list)
        createdAt = datetime.utcnow()
        for group in group_list:
            group['createdAt'] = createdAt
            group['lower_name'] = group['name'].lower()
        return await self.collection_group_list.insert_many(group_list)
    
    async def delete_grouplist(self):
        return await self.collection_group_list.delete_many({})

    async def count_group_list(self):
        return await self.collection_group_list.estimated_document_count()

    async def get_group_by_id(self, group_id):
        return await self.collection_group_list.find_one({'id':int(group_id)})
    async def get_group_by_name(self, group_name):
        return await self.collection_group_list.find_one({'lower_name':group_name.lower()})

    async def create_english_groups(self, enslish_group_list):
        createdAt = datetime.utcnow()
        groups_to_db = []
        for group in enslish_group_list:
            group_to_db = dict()
            group_to_db['createdAt'] = createdAt
            group_to_db['number'] = group
            groups_to_db.append(group_to_db)
            
        return await self.collection_english_group_list.insert_many(groups_to_db)
    async def delete_english_group_list(self):
        return await self.collection_english_group_list.delete_many({})
    async def count_engslish_group_list(self):
        return await self.collection_english_group_list.estimated_document_count()
    async def find_english_group(self, group_num):
        return await self.collection_english_group_list.find_one({"number": group_num})
    async  def add_user_to_push(self,user_push: UserPush):
        response = await self.collection_users_with_push.find_one({"sub": user_push.sub})
        if response:
            return await self.collection_users_with_push.update_one({"sub": user_push.sub},
             {"$set":
                                         {"hour": user_push.hour,
                                          "minute": user_push.minute,
                                          "isActive": user_push.isActive
                                          }

                                     })
        else:
             return  await self.collection_users_with_push.insert_one(dict(user_push))
       
    def get_subs_for_push(self, hour: int):
       return self.collection_users_with_push.find({'hour':hour, 'isActive': True})

    def async_get_push_info_user(self, sub: str):
        return self.collection_users_with_push.find_one({'sub': sub}) 