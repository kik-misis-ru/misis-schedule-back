from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    group_id: str
    subgroup_id: str
    eng_group: int
