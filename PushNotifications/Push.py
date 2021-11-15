
from datetime import  datetime
from pathlib import Path
from scheme import *
from Schedule.schedule import *
from User.user import *
from utils import Days, Bells
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
heroku_time_diff = os.getenv("HEROKU_TIME_DIFF")
client = AsyncIOMotorClient(url)



async def get_data_for_push(sub):
	response = dict()
	user_data = await get_user(sub)
	if(user_data == "0"):
		response["status"] = status_code_not_found
		return response
	count_lessons = 0
	start_time = ""
	current_date = datetime.today() + timedelta(hours=int(heroku_time_diff))
	day_num = current_date.isoweekday()
	if (day_num == 6):
		response["day"] = "Завтра"
		response["count_lessons"] = 0
		response["lesson"] = "пар"
		response["start_time"] = "0"
		response["status"] = status_code_success
		return response

	teacher_id = user_data["teacher_id"]
	if teacher_id!=None and teacher_id!="":
		scheduleData = await get_teacher_schedule(teacher_id, current_date.strftime("%Y-%m-%d"))
	else:
		group_id = user_data["group_id"]
		scheduleData = await get_schedule(group_id, "",  datetime.today().strftime("%Y-%m-%d"))
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

	



