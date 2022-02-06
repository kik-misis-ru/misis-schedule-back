import gspread
from utils import *
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class English:

    def __init__(self):
        url = os.getenv("MONGO_CONNECTION_STRING")
        client = AsyncIOMotorClient(url)
        db = client.get_database("schedule")
        self.collection_english = db.get_collection("schedule_english")
        self.english_subject_id=5781
        #collection_english.create_index( "group_id", unique= True )

        self.google_sheets_files = [os.getenv("FIRST_COURSE_TECH_BACHELOR_ENGLISH"),
                       os.getenv("SECOND_COURSE_TECH_BACHELOR_ENGLISH"),
                       os.getenv("THIRD_COURSE_TECH_BACHELOR_ENGLISH"),
                       os.getenv("FOURTH_COURSE_TECH_BACHELOR_ENGLISH")]


    #возвращает расписание по английскому, получанное из google-файла или из БД
    def get_enslish_schedule(self, group_id):
        if not group_id:
            return -1
        gc = gspread.service_account(filename='creds.json')
        course_number = int(group_id[0])
        if course_number<=0 or course_number>4:
            for course in range(4):
                schedule = self.find_schedule_in_couse_file(course, group_id, gc)
                if schedule != -1:
                    return schedule
            return -1
        else:
            return self.find_schedule_in_couse_file(course_number, group_id, gc)
        

    #поиск нужного расписания в файле для конкретного курса
    def find_schedule_in_couse_file(self, course_number: int, group_id: int, gc):
        google_sheet_file = self.google_sheets_files[course_number-1]
        sh = gc.open_by_key(google_sheet_file)
        nums = [str(i) for i in range(1,32)]
        for sheet in sh:
            table = sheet.get_all_values()
            for row in table[4:]:
                if(len(row)==0):
                    continue
                is_row_group = False
                start_group_column = 0
                for i in range(0,len(row),3):
                    if i< len(row)-3:
                        if row[i] not in nums:
                            is_row_group = True
                            start_group_column=i
                            break
                if is_row_group:
                    for i in range(start_group_column, len(row), 3):
                        if row[i] and len(row[i])>2:
                            group = row[i].split(' ')[0].strip()
                            print(group)
                            if(str(group)==str(group_id) and len(row)>i+2):
                                teacher = row[i + 1].strip()
                                teacher=formate_teacher_initials(teacher)
                                classes = row[i + 2].split('-')
                                sch = Sch(group, teacher, classes)
                                return sch       
        return -1

    #встраивает расписание по английскому в основное расписание
    def set_english_info_to_schedule(self, schedule_dict, eng_schedule):
        if schedule_dict and "schedule" in schedule_dict:
            schedule = schedule_dict["schedule"]
            if not schedule:
                return schedule_dict
            count=0
            for bell in Bells:
                if not bell in schedule:
                    continue
                schedule_bell = schedule[bell]
                for day in Days:
                    if not day in schedule_bell:
                        continue
                    schedule_day = schedule_bell[day]
                    if len(schedule_day["lessons"])==0:
                        continue
                    for i in range(len(schedule_day["lessons"])):
                        lesson = schedule_day["lessons"][i]
                        if  lesson["subject_id"]== self.english_subject_id:
                            if(len(eng_schedule['classes'])>count):
                                lesson["room_name"]=eng_schedule['classes'][count]
                            if(len(lesson['teachers'])>0):
                                lesson['teachers'][0]['name']=eng_schedule['teacher']
                            if(len(lesson['rooms'])>0):
                                if(len(eng_schedule['classes'])>count):
                                    lesson['rooms'][0]['name']=eng_schedule['classes'][count]
                            count+=1
        return schedule_dict
    
    #выполняет получение расписания по английскому и встраивание его в основное расписание
    async def add_english_schedule(self, schedule_dict, eng_group_id):
        response = await self.collection_english.find_one({"group_id": str(eng_group_id)})
        if response:
            schedule_dict =self.set_english_info_to_schedule(schedule_dict, response)
            return schedule_dict
        else:
            english_schedule= self.get_enslish_schedule(eng_group_id)
            if english_schedule ==-1:
                return schedule_dict
            english_schedule_dict =dict()
            english_schedule_dict['group_id']=english_schedule.group_id
            english_schedule_dict['teacher']=english_schedule.teacher
            english_schedule_dict['classes']=english_schedule.classes
            english_schedule_dict["createdAt"] = datetime.utcnow()
            schedule_dict = self.set_english_info_to_schedule(schedule_dict, english_schedule_dict)
            self.collection_english.insert_one(english_schedule_dict)
            return schedule_dict

    def get_all_english_groups(self):
        gc = gspread.service_account(filename='creds.json')
        group_list = []
        for course in self.google_sheets_files:
            sh = gc.open_by_key(course)
            nums = [str(i) for i in range(1,32)]
            for sheet in sh:
                table = sheet.get_all_values()
                for row in table[4:]:
                    if(len(row)==0):
                        continue
                    is_row_group = False
                    for i in range(0,len(row),3):
                        if i< len(row)-3:
                            if row[i] not in nums:
                                is_row_group = True
                                break
                    if is_row_group:
                        for i in range(0, len(row), 3):
                            if row[i] and len(row[i])>2:
                                group = row[i].split(' ')[0].strip()
                                group_list.append(group)     
        return group_list



    


    





