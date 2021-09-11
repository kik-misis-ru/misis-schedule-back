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
