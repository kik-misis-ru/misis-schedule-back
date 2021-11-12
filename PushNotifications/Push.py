
from datetime import  datetime
from pathlib import Path
from scheme import *
from Schedule.schedule import *
from User.user import *
from utils import Days, Bells

async def get_data_for_push(sub):
	user_data = await get_user(sub)
	if(user_data == 0):
		return status_code_not_found
	group_id = user_data["group_id"]
	count_lessons = 0
	start_time =""
	day_num = datetime.today().isoweekday()
	day_schedule = Days[day_num] 
	scheduleData = await get_schedule(group_id, "",  datetime.today().strftime("%Y-%m-%d"))
	schedule = scheduleData["schedule"]
	for bell in Bells:
		if(bell in schedule):
			day = schedule[bell][day_schedule]
			if(len(day["lessons"])):
				count_lessons+=1
				if(start_time==""):
					start_time = schedule[bell]["header"]["start_lesson"]
	templateData = PushTemplate("Завтра", count_lessons, "пар", start_time)
	return templateData

	



