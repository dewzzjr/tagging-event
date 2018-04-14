# -*- coding: utf-8 -*-
import firebase_admin
from firebase_admin import db, credentials
from datetime import datetime
from .adb import AbstractDB
import dateutil.parser


class FirebaseDB(AbstractDB):
    def __init__(self, config):
        super().__init__(config)
        
        if 'FIREBASE' in self.config:
            cred = credentials.Certificate(self.config['FIREBASE']['CERT'])
            firebase_admin.initialize_app(cred, {
                'databaseURL' : self.config['FIREBASE']['DSN']
            })
            self.fb = db.reference('dataset')
        else:
            self.fb = None
            self._check_status()
            
    def _check_status(self):
        if self.fb is None:
            print("no firebase")
            raise NameError
    
    def getAll(self):
        return self.fb.get()
    
    def getEntries(self, lastKey, limit):
        if lastKey is None:
            return self.fb.limit_to_first(limit).get()
        return self.fb.start_at(lastKey).limit_to_first(limit).get()
    
    def _get(self, id):
        return self.fb.child(id)
    
    def getId(self, id):
        return self._get(id).get()
    
    def putData(self, data):
        token = self._get(data['_id'])
        token.update(data)
        
    # data = {'_id':[YOUR_ID],'index':[TAG_INDEX],'tag':[TAG_NAME]}
    def setData(self, data):
        token = self._get(data['_id'])
        token.child('label').update({data['index']:data['tag']})
        
    def setType(self, id, type):
        token = self._get(id)
        token.update({'type':type})
        
    def removeType(self, id):
        token = self._get(id)
        token.child('type').remove()
        
    def setTimestamp(self, id):
        token = self._get(id)
        token.update({'timestamp':datetime.now()})
        
    def getTimestamp(self, id):
        token = self._get(id).child('timestamp').get()
        try:
            time = dateutil.parser.parse(token)
        except TypeError:
            return None
        # print(time)
        return time;