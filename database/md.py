# -*- coding: utf-8 -*-
from pymongo import MongoClient 
from datetime import datetime
from .adb import AbstractDB
import dateutil.parser
import os

IS_PROD = os.environ.get('IS_HEROKU', None)
DEFAULT_DATASET = 'newdataset0'
DEFAULT_DB_NAME = 'datasets'

class MongoDB(AbstractDB):
    def __init__(self, config, config_name = 'MONGO', db_name = DEFAULT_DB_NAME, dataset = DEFAULT_DATASET):
        self.dataset = dataset
        self.db_name = db_name
        super().__init__(config)
        if IS_PROD:
            mongo_host = os.environ.get('MONGO_HOST', None)
            mongo_user = os.environ.get('MONGO_USER', None)
            mongo_pass = os.environ.get('MONGO_PASS', None)
            self.mongo = MongoClient('mongodb+srv://'+mongo_user+':'+mongo_pass+'@'+mongo_host+'/'+db_name)
        else:
            if config_name in self.config:
                mongo_host = self.config[config_name]['HOST']
                mongo_port = int(self.config[config_name]['PORT'])
                if 'USER' in self.config[config_name]:
                    mongo_user = self.config[config_name]['USER']
                    mongo_pass = self.config[config_name]['PASS']
                    print('mongodb+srv://'+mongo_user+':'+mongo_pass+'@'+mongo_host+'/'+db_name)
                    self.mongo = MongoClient('mongodb+srv://'+mongo_user+':'+mongo_pass+'@'+mongo_host+'/'+db_name)
                    
                else:
                    self.mongo = MongoClient(mongo_host, mongo_port)
                print("init mongo")
            else:
                self.mongo = None
                self._check_status()
            
    
    def _check_status(self):
        if self.mongo is None:
            print("no mongo")
            raise NameError
            
    
    def getEntries(self, offset, limit):
        return self.getAll().skip(offset).limit(limit)
    
    def getAll(self):
        return self.mongo[self.db_name][self.dataset].find()
    
    def getId(self, id):
        return self.mongo[self.db_name][self.dataset].find_one({'_id':id})
        
    
    def getTimestamp(self, id):
        data = self.getId(id)
        try:
            time = dateutil.parser.parse(data['timestamp'])
        except TypeError:
            return None
        return time
    
    # data = {'_id':[YOUR_ID],'index':[TAG_INDEX],'tag':[TAG_NAME]}
    def setData(self, data):
        updateData = { '$set': { 'label.'+str(data['index']):data['tag'] } }
        self.mongo[self.db_name][self.dataset].update_one({'_id': data['_id']}, updateData)
        
    def setType(self, id, type):
        updateData = { '$set': { 'type':type } }
        self.mongo[self.db_name][self.dataset].update_one({'_id': id}, updateData)
        
    def removeType(self, id):
        updateData = { '$unset': { 'type': 1 } }
        self.mongo[self.db_name][self.dataset].update_one({'_id': id}, updateData)
        
        
    def putData(self, data):
        self.mongo[self.db_name][self.dataset].insert_one(data)
        
    def setTimestamp(self, id):
        updateData = { '$set': { 'timestamp':datetime.now() } }
        self.mongo[self.db_name][self.dataset].update_one({'_id': id}, updateData)