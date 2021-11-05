from requests.models import Response, requote_uri
from pydantic.networks import import_email_validator
from english import get_enslish_schedule
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from scheme import *
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
from utils import *
from english import *
from  DataBase.mongo import MongoRepository

mongo_repository = MongoRepository()


async def get_schedule(group_id, english_group_id, date):
    date_monday =  get_monday(date)
    response = await mongo_repository.get_schedule(group_id, date_monday)
    
    if response:
        response = await  add_english_schedule(dict(response), english_group_id)
        response["createdAt"] = str(response["createdAt"])
        return response
    else:
        schedule = get_schedule(group_id, date_monday)
        schedule["createdAt"] = str(datetime.utcnow())      
        mongo_repository.create_schedule(schedule)
        schedule_dict = await add_english_schedule(dict(schedule), english_group_id)
        return schedule_dict