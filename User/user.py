from starlette import status
from scheme import *
from Schedule.schedule import *
from DataBase.mongo import MongoRepository

class User:
    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
        self.schedule = Schedule(mongo_repository)
        load_dotenv(dotenv_path=env_path)
        self.heroku_time_diff  = os.getenv("HEROKU_TIME_DIFF")

    async def add_user(self, user: UserModel):
        if await self.mongo_repository.find_user(user.user_id) is None:
            result = await self.mongo_repository.create_user(dict(user))
            if result.inserted_id:
                return status.HTTP_201_CREATED
            else:
                return status.HTTP_500_INTERNAL_SERVER_ERROR 
        else:
            result = await self.mongo_repository.update_user(user)
            if result.modified_count == 1:
                return status.HTTP_201_CREATED
            else:
                return status.HTTP_500_INTERNAL_SERVER_ERROR
    async def get_user(self, user_id: str):
        response = await self.mongo_repository.find_user(user_id)
        if response:
            result = get_user_info(response)
            return result
        else:
            return "0"

    async def add_user_to_push(self, user_push: UserPush):
        result = await self.mongo_repository.add_user_to_push(user_push)
        response = dict()
        if result.acknowledged:
            response["status"] = status_code_success
        else:
            response["status"] = status_code_error
        return  response

    async def get_subs_for_push(self, hour: int):
        subs =  self.mongo_repository.get_subs_for_push(hour)
        subslist = await subs.to_list(None)
        data = []
        for sub in subslist:
            del sub['_id']
            data.append(sub)
        return data

    async def get_data_for_push(self, sub):
        response = dict()
        user_data = await self.get_user(sub)
        if(user_data == "0"):
            response["status"] = status_code_not_found
            return response
        count_lessons = 0
        start_time = ""
        current_date = datetime.today() + timedelta(hours=int(self.heroku_time_diff))
        day_num = current_date.isoweekday()
        if (day_num == 6):
            response["day"] = "Завтра"
            response["count_lessons"] = 0
            response["lesson"] = "пар"
            response["start_time"] = "0"
            response["status"] = status_code_success
            return response
        if day_num==7:
            day_num = 0
            current_date = current_date + timedelta(hours=24)
        teacher_id = user_data["teacher_id"]
        if teacher_id!=None and teacher_id!="":
            scheduleData = await self.schedule.get_teacher_schedule(teacher_id, current_date.strftime("%Y-%m-%d"))
        else:
            group_id = user_data["group_id"]
            scheduleData = await self.schedule.get_schedule(group_id, "",  datetime.today().strftime("%Y-%m-%d"))
        day_schedule = Days[day_num] 
        if scheduleData and "status" in scheduleData and scheduleData["status"] == "FOUND":
            schedule = scheduleData["schedule"]
            for bell in Bells:
                if(bell in schedule):
                    day = schedule[bell][day_schedule]
                    if len(day["lessons"]):
                        count_lessons+=1
                        if(start_time==""):
                            start_time = schedule[bell]["header"]["start_lesson"]
        response["day"] = "Завтра"
        response["count_lessons"] = count_lessons
        if count_lessons == 1:
            response["lesson"] = "пара"
        elif count_lessons in (2,3,4):
            response["lesson"] = "пары"
        else:
            response["lesson"] = "пар"
        response["start_time"] = start_time
        response["status"] = status_code_success
        return response