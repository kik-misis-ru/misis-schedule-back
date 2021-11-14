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
    print("response:", response)
    if response:
        result = get_user_info(response)
        return result
    else:
        return "0"

async def add_user_to_push(user_push: UserPush):
    result = await mongo_repository.add_user_to_push(user_push)
    response = dict()
    if result.acknowledged:
        response["status"] = status_code_success
    else:
        response["status"] = status_code_error
    return  response

async def get_subs_for_push(hour: int):
    subs =  mongo_repository.get_subs_for_push(hour)
    subslist = await subs.to_list(None)
    data = []
    for sub in subslist:
        del sub['_id']
        data.append(sub)
    return data