from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime
import motor
from motor.motor_asyncio import AsyncIOMotorClient

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

    async def get_schedule(self, group_id, date_monday):
        return await self.collection_schedule.find_one({"group_id": str(group_id), "start_date": str(date_monday)})
    
    def create_schedule(self, schedule):
        self.collection_schedule.insert_one(schedule)

    async def get_schedule_teacher(self, teacher_id, date_monday):
        return await self.collection_schedule_teacher.find_one({"teacher_id": str(teacher_id), "start_date":str(date_monday)})
    
    def create_teacher_schedule(self, schedule):
        self.collection_schedule_teacher.insert_one(schedule)

    async def find_user(self, user_id):
        return await self.collection_users.find_one({"user_id": user_id})

    def create_user(self, user):
        self.collection_users.insert_one(user)
    
    def update_user(self, user):
        self.collection_users.update_one({"user_id": user.user_id},
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
        return await self.collection_teachers.find_one({'last_name': fio.last_name, 'first_name': fio.first_name, 'mid_name':fio.mid_name})
    
    async def find_teacher_id(self, teacher_id):
        return await self.collection_teachers.find_one({'id':teacher_id})

    def create_grouplist(self, groups_info):
        createdAt = datetime.utcnow()
        print(groups_info)
        for group_info in groups_info:
            group_info['createdAt'] = createdAt
            
        self.collection_group_list.insert_many(groups_info)
