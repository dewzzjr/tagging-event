# -*- coding: utf-8 -*-
# contoh data:
# entries = [
#            {
#                '_id':1,
#                'text' : [ 'lorem', 'ipsum',  'dolor' ],
#                'label': [ 'O',     'B-TIME', 'O'     ],
#                'timestamp': 2018-03-29 15:11:09.130000,
#                'type': 'bazaar'
#            },
#            {
#                '_id':2,
#                'text' : [ 'lorem', ',', 'ipsum',   'dolor'   ],
#                'label': [ 'O',     'O', 'B-PLACE', 'I-PLACE' ],
#                'timestamp': 2018-05-16 10:40:10.674000,
#                'type': 'pendidikan'
#            },
#            {
#                '_id': 3,
#                'text' : [ 'lorem',  'ipsum',  'dolor', 'sit', '?' ],
#                'label': [ 'B-NAME', 'B-TIME', 'O',     'O',   'O' ],
#                'timestamp': 2018-05-16 10:41:48.999000,
#            }
#        ]

from pymongo import MongoClient, errors 
from datetime import datetime
from .adb import AbstractDB
import dateutil.parser
import os

IS_PROD = os.environ.get('IS_HEROKU', None)
DEFAULT_DATASET = 'newdataset1'
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
        try:
            self.mongo[self.db_name][self.dataset].insert_one(data)
        except errors.DuplicateKeyError:
            updateData = {'$set': data}
            self.mongo[self.db_name][self.dataset].update_one(
                {'_id': data['_id']}, updateData)
        
    def setTimestamp(self, id):
        updateData = { '$set': { 'timestamp':datetime.now() } }
        self.mongo[self.db_name][self.dataset].update_one({'_id': id}, updateData)

    def insertTagged(self, id):
        try:
            self.mongo['status']['tagged'].insert_one({'_id': id})
        except errors.DuplicateKeyError:
            pass
        
    def removeTagged(self, id):
        self.mongo['status']['tagged'].remove({"_id":id})

    def getTagged(self):
        datas = []

        for data in self.mongo['status']['tagged'].find():
            datas.append(data['_id'])
        result = self.mongo[self.db_name][self.dataset].find(
            {'_id': {'$in': datas}})
        return result
