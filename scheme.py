from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    filial_id: str
    group_id: str
    subgroup_name: str
    eng_group: str
    teacher_id: str
    
class FIO(BaseModel):
    last_name: str
    first_name: str
    mid_name: str

class SubGroup():
    def __init__(self, Bell, Day, Lesson, Subject_id, Lesson_num, Group_num):
        self.bell=Bell
        self.day=Day
        self.lesson=Lesson
        self.subject_id=Subject_id
        self.lesson_num = Lesson_num
        self.group_num = Group_num
    bell: str
    day: str
    subGroup: int
    subject_id: int
    lesson_num: int
    group_num: int

class Sch:
    def __init__(self, Group_Id, Teacher, Classes):
        self.group_id = Group_Id
        self.teacher = Teacher
        self.classes = Classes
    group_id: int
    teacher: str
    classes = []

class PushTemplate:
    def __init__(self, day, count_lessons, lesson, start_time):
        self.day=day
        self.count_lesson=count_lessons
        self.lesson=lesson
        self.start_time=start_time
    day: str
    count_lesson: str
    lesson: str
    start_time: str

class UserPush(BaseModel):
    sub: str
    hour: int
    minute: int
    isActive: bool
    day: int

class DataForPush(BaseModel):
    sub:str