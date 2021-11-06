
from scheme import *
from utils import *
from English.english import *
from Database.mongo import MongoRepository

mongo_repository = MongoRepository()


async def group_by_id(group_id):
    response = dict()
    group = await mongo_repository.get_group_by_id(group_id)
    if group:
         response['id'] = group['id']
         response['name'] = group['name']
         response["status"]= status_code_success
         return response
    else:
        response["status"] = status_code_not_found
        return response

async def group_by_name(name):
    response = dict()
    group = await mongo_repository.get_group_by_name(name)
    if group:
         response['id'] = group['id']
         response['name'] = group['name']
         response["status"]= status_code_success
         return response
    else:
        response = dict()
        response["status"] = status_code_not_found
        return response

async def is_english_group_exist(group_num):
    group = await mongo_repository.find_english_group(group_num)
    response = dict()
    if(group):
        response["status"] = status_code_success
    else:
        response["status"] = status_code_not_found
    return response

async def load_english_groups():
    response = dict()
    delete_result = await mongo_repository.delete_english_group_list()
    if(delete_result.deleted_count==0):
        count_rows = await mongo_repository.count_engslish_group_list()
        if(count_rows!=0):
            response["status"] = status_code_error
            return response
    groups = get_all_english_groups()
    insert_result = await mongo_repository.create_english_groups(groups)
    if(len(insert_result.inserted_ids)>0):
        response["status"] = status_code_success
    else:
        response["status"] = status_code_error
    return response

async def load_groups():
    response = dict()
    delete_result = await mongo_repository.delete_grouplist()
    if(delete_result.deleted_count==0):
        count_rows = await mongo_repository.collection_group_list()
        if(count_rows!=0):
            response["status"] = status_code_error
            return response
    groups = get_groups()
    insert_result = await mongo_repository.create_grouplist(groups)
    
    if(len(insert_result.inserted_ids)>0):
        response["status"] = status_code_success
    else:
        response["status"] = status_code_error
    return response