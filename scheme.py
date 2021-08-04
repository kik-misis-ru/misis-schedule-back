from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    filial_id: str
    group_id: str
    subgroup_name: str
    eng_group: str
