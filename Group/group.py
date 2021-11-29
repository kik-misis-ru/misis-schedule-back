
from scheme import *
from utils import *
from English.english import *
from DataBase.mongo import MongoRepository




class Group:
    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
        self.english = English()

    async def group_by_id(self,group_id):
        response = dict()
        if group_id == "NaN":
            response["status"] = status_code_not_found
            return response
        group = await self.mongo_repository.get_group_by_id(group_id)
        if group:
            response['id'] = group['id']
            response['name'] = group['name']
            response["status"]= status_code_success
            return response
        else:
            response["status"] = status_code_not_found
            return response

    async def group_by_name(self,name: str):
        name = name.strip()
        response = dict()
        group = await self.mongo_repository.get_group_by_name(name)
        if group:
            response['id'] = group['id']
            response['name'] = group['name']
            response["status"]= status_code_success
            return response
        else:
            response = dict()
            response["status"] = status_code_not_found
            return response

    async def is_english_group_exist(self, group_num):
        group = await self.mongo_repository.find_english_group(group_num)
        response = dict()
        if(group):
            response["status"] = status_code_success
        else:
            response["status"] = status_code_not_found
        return response

    async def load_english_groups(self):
        response = dict()
        delete_result = await self.mongo_repository.delete_english_group_list()
        if(delete_result.deleted_count==0):
            count_rows = await self.mongo_repository.count_engslish_group_list()
            if(count_rows!=0):
                response["status"] = status_code_error
                return response
        groups = self.english.get_all_english_groups()
        insert_result = await self.mongo_repository.create_english_groups(groups)
        if(len(insert_result.inserted_ids)>0):
            response["status"] = status_code_success
        else:
            response["status"] = status_code_error
        return response

    async def load_groups(self):
        response = dict()
        delete_result = await self.mongo_repository.delete_grouplist()
        if(delete_result.deleted_count==0):
            count_rows = await self.mongo_repository.collection_group_list()
            if(count_rows!=0):
                response["status"] = status_code_error
                return response
        groups = get_groups()
        insert_result = await self.mongo_repository.create_grouplist(groups)
    
        if(len(insert_result.inserted_ids)>0):
            response["status"] = status_code_success
        else:
            response["status"] = status_code_error
        return response