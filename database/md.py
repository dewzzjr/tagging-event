# -*- coding: utf-8 -*-
from pymongo import MongoClient 
from sshtunnel import SSHTunnelForwarder
from datetime import datetime
from .adb import AbstractDB
import dateutil.parser

DEFAULT_DATASET = 'newdataset0'
DEFAULT_DB_NAME = 'datasets'

class MongoDB(AbstractDB):
    def __init__(self, config, config_name = 'MONGO', db_name = DEFAULT_DB_NAME, dataset = DEFAULT_DATASET):
        self.dataset = dataset
        self.db_name = db_name
        super().__init__(config)
        if config_name in self.config:
            mongo_host = self.config[config_name]['HOST']
            mongo_port = int(self.config[config_name]['PORT'])
            if 'USER' in self.config[config_name]:
                mongo_user = self.config[config_name]['USER']
                mongo_pass = self.config[config_name]['PASS']
#                server = SSHTunnelForwarder(
#                    mongo_host,
#                    ssh_username=mongo_user,
#                    ssh_password=mongo_pass,
#                    remote_bind_address=('127.0.0.1', mongo_port)
#                )
#                server.start()
#                self.mongo = MongoClient('127.0.0.1', server.local_bind_port)
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
    
    def setData(self, data):
        updateData = {
                      '$set': {
                              'label.'+data['index']:data['tag']
                              }
                      }
        self.mongo[self.db_name][self.dataset].update_one({'_id': data['_id']}, updateData)
        
    def putData(self, data):
        self.mongo[self.db_name][self.dataset].insert_one(data)
        
    def setTimestamp(self, id):
        updateData = {
                      '$set': {
                              'timestamp':datetime.now()
                              }
                      }
        self.mongo[self.db_name][self.dataset].update_one({'_id': id}, updateData)