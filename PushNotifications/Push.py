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


load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
send_push_url = os.getenv("SEND_PUSH_URL")
auth_sber_url = os.getenv("AUTH_SBER_URL")
client_id_secret_id_base64 = os.getenv("CLIENT_ID_CLIENT_SECRET_BASE64")
project_id_sber_code=os.getenv("PROJECT_ID_SBER_CODE")
app_id_sber_code=os.getenv("APP_ID_SBER_CODE")
version_id_app_sber_code=os.getenv("VERSION_ID_APP_SBER_CODE")


def push():
    sub = "noN0Crr3wgIDB0zPleKresJJBnQWbTybFS96aH/CO1ag1UKZFmqfjY9pgDfQAAv8DJiarMJBCd+OSKUzNTk2jw0W/jbBIC6V/xwQdmSX5cA3bAbhWkZVtK9z3zFc8Mkh3O1nZa/qn3SAagVDNjZIB6p4Z9Wzb0Lm/uzDjpy3qh0="
    templateData = PushTemplate("Завтра", "5", "пар", "9:00")
    start_time = datetime.now() + timedelta(minutes=1)
    finish_time = datetime.now() +timedelta(minutes=2)
    start_date = datetime.today()
    end_date =datetime.today()
    send_push(sub, templateData, start_time, finish_time, start_date, end_date)

def run_push():
	while(True):
		#push()
		time.sleep(100)

def send_push(sub: str, templateData: PushTemplate, start_time: datetime, finish_time: datetime, start_date: date, end_date:date):
    data = get_body_for_send_push(sub, templateData, start_time, finish_time, start_date, end_date)
    headers={'Authorization': 'Bearer '+get_auth_token(), 'Content-type': 'application/json', 'RqUID': get_guid()}

    response = requests.post(send_push_url, data=json.dumps(data), headers=headers)
    
    print(response.status_code)

def get_auth_token():
    headers={'Authorization': 'Basic '+client_id_secret_id_base64, 'Content-type': 'application/x-www-form-urlencoded', 'RqUID': get_guid()}
    data={'scope': 'SMART_PUSH'}
    response = requests.post(auth_sber_url, data=data, headers=headers)
    return response.json()['access_token']
    


def get_guid():
    return  str(uuid.uuid4())

def get_body_for_send_push(sub: str, templateData: PushTemplate, start_time: datetime, finish_time: datetime, start_date: date, end_date:date):
	body = {
	"requestPayload": {
		"protocolVersion": "V1",
		"messageId": 37284759,#random.randint(0, 1000000),
		"messageName": "SEND_PUSH",
		"payload": {
			"sender": {
                "projectId":project_id_sber_code,
				"application": {
					"appId": app_id_sber_code,
					"versionId": version_id_app_sber_code
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
								"count_lessons": templateData.count_lesson,
								"lesson": templateData.lesson,
                                "start_time":templateData.start_time
							},
							"mobileAppParameters": {
							},
							"timeFrame": {
								"startTime": start_time.strftime("%H:%M:%S"),
								"finishTime": finish_time.strftime("%H:%M:%S"),
								"timeZone": "GMT+03:00",
								"startDate": start_date.strftime("%Y:%m:%d"),
								"endDate": end_date.strftime("%Y:%m:%d")
							}
						}
					}
				]
			}
		}
	}
	}
	return body