import requests
from datetime import date, datetime, timedelta
from pathlib import Path
import os
import json
from scheme import *
from requests.api import request
import random
from dotenv import load_dotenv
import uuid
import time
import Schedule
from DataBase.mongo import MongoRepository
from Schedule.schedule import *
from User.user import *
from utils import Days, Bells
# mongo_repository = MongoRepository()
from main import mongo_repository


load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
send_push_url = os.getenv("SEND_PUSH_URL")
auth_sber_url = os.getenv("AUTH_SBER_URL")
client_id_secret_id_base64 = os.getenv("CLIENT_ID_CLIENT_SECRET_BASE64")
project_id_sber_code=os.getenv("PROJECT_ID_SBER_CODE")


async def push(data):
	sub = data["sub"]
	templateData = await get_data_for_push(sub)
	start_time = datetime.today()
	start_time = start_time.replace(hour=data['hour'], minute=data['minute'], second=0, microsecond=0)
	finish_time = start_time + timedelta(minutes=1)
	start_date = datetime.today()
	end_date = start_date
	await get_data_for_push(sub)
	send_push(sub, templateData, start_time, finish_time, start_date, end_date)

async def run_push():
	start = datetime.now()
	push_hour = datetime.now().hour + 1
	#subs =  mongo_repository.get_subs_for_push(push_hour)
	#subslist = await subs.to_list(None)
	#for sub in subslist:
	#	await push(sub)
	delta = datetime.now() -start
	time.sleep(3600 - delta.total_seconds())


def send_push(sub: str, templateData: PushTemplate, start_time: datetime, finish_time: datetime, start_date: date, end_date:date):
    data = get_body_for_send_push(sub, templateData, start_time, finish_time, start_date, end_date)
    headers={'Authorization': 'Bearer '+get_auth_token(), 'Content-type': 'application/json', 'RqUID': get_guid()}

    response = requests.post(send_push_url, data=json.dumps(data), headers=headers)
    
    print(response.text)

def get_auth_token():
    headers={'Authorization': 'Basic '+client_id_secret_id_base64, 'Content-type': 'application/x-www-form-urlencoded', 'RqUID': get_guid()}
    data={'scope': 'SMART_PUSH'}
    response = requests.post(auth_sber_url, data=data, headers=headers)
    return response.json()['access_token']
    


def get_guid():
	guid = str(uuid.uuid4())
	return guid

def get_body_for_send_push(sub: str, templateData: PushTemplate, start_time: datetime, finish_time: datetime, start_date: date, end_date:date):
	body = {
	"requestPayload": {
		"protocolVersion": "V1",
		"messageId": random.randint(0, 1000000),
		"messageName": "SEND_PUSH",
		"payload": {
			"sender": {
                "projectId":project_id_sber_code,
				"application": {
					"appId": project_id_sber_code,
					"versionId": project_id_sber_code
				}
			},
			"recipient": {
				"clientId": {
					"idType": "SUB",
					"id": sub
				}
			},
			"deliveryConfig": {
				"deliveryMode": "BROADCAST",
				"destinations": [{
						"channel": "COMPANION_B2C",
						"surface": "COMPANION",
						"templateContent": {
							"id": "935f93f9-002b-4265-88ec-75de24ce6a99",
							"headerValues": {
							},
							"bodyValues": {
							    "day": templateData.day,
								"count_lessons": str(templateData.count_lesson),
								"lesson": templateData.lesson,
                                "start_time":templateData.start_time
							},
							"mobileAppParameters": {
							},
							"timeFrame": {
							 	"startTime": start_time.strftime("%H:%M:%S"),
							 	"finishTime": finish_time.strftime("%H:%M:%S"),
							 	"timeZone": "GMT+03:00",
							 	"startDate": start_date.strftime("%Y-%m-%d"),
							 	"endDate": end_date.strftime("%Y-%m-%d")
							 }
						}
					}
				]
			}
		}
	}
	}
	return body


async def get_data_for_push(sub):
	user_data = await get_user(sub)
	group_id = user_data["group_id"]
	count_lessons = 0
	start_time =""
	day_num = datetime.today().isoweekday()
	day_schedule = Days[day_num] 
	sub_group = user_data["subgroup_name"]
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

	



