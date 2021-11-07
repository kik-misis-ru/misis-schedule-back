from scheme import *
from Schedule.schedule import *
from DataBase.mongo import MongoRepository

mongo_repository = MongoRepository()
async def add_user(user: User):
    if await mongo_repository.find_user(user.user_id) is None:
        mongo_repository.create_user(dict(user))
    else:
        mongo_repository.update_user(user)

async def get_user(user_id: str):
    response = await mongo_repository.find_user(user_id)
    if response:
        result = get_user_info(response)
        return result
    else:
        return "0"