
from datetime import  datetime
from pathlib import Path
from scheme import *
from Schedule.schedule import *
from User.user import *
from utils import Days, Bells

async def get_data_for_push(sub):
	response = dict()
	user_data = await get_user(sub)
	if(user_data == "0"):
		response["status"] = status_code_not_found
		return response
	group_id = user_data["group_id"]
	count_lessons = 0
	start_time =""
	day_num = datetime.today().isoweekday()
	day_schedule = Days[day_num] 
	scheduleData = await get_schedule(group_id, "",  datetime.today().strftime("%Y-%m-%d"))
	if "status" in scheduleData and scheduleData["status"] == "FOUND":
		schedule = scheduleData["schedule"]
		for bell in Bells:
			if(bell in schedule):
				day = schedule[bell][day_schedule]
				if(len(day["lessons"])):
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

	



