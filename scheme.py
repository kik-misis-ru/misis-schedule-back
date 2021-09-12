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