# -*- coding: utf-8 -*-
#from firebase import firebase
import firebase_admin
from firebase_admin import db, credentials
from datetime import datetime
from .adb import AbstractDB
import dateutil.parser

#
#class FirebaseDB(AbstractDB):
#    def __init__(self, config):
#        super().__init__(config)
#        print(self.config)
#        if 'FIREBASE' in self.config:
#            self.fb = firebase.FirebaseApplication(self.config['FIREBASE']['DSN'], None)
#            print("init firebase")
#        else:
#            self.fb = None
#            self._check_status()
#            
#    def _check_status(self):
#        if self.fb is None:
#            print("no firebase")
#            raise NameError
#    
#    def getAll(self):
#        return list(self.fb.get('/dataset/', None).values())
#    
#    def getEntries(self, offset, limit):
#        entries = self.getAll()
#        return entries[offset:offset+limit]
#    
#    def getId(self, id):
#        return self.fb.get('/dataset/', id)
#    
#    def setData(self, data):
#        url = '/dataset/' + data['_id'] + '/label'
#        self.fb.put(url,
#                    name=data['index'],
#                    data=data['tag'],
#                    params={'print': 'pretty'}, 
#                    headers={'X_FANCY_HEADER': 'VERY FANCY'})
#        
#    def setTimestamp(self, id):
#        url = '/dataset/' + id
#        self.fb.put(url,
#                    name='timestamp',
#                    data=datetime.now(),
#                    params={'print': 'pretty'}, 
#                    headers={'X_FANCY_HEADER': 'VERY FANCY'})
#        
#    def getTimestamp(self, id):
#        data = self.fb.get('/dataset/' + id, 'timestamp')
#        try:
#            time = dateutil.parser.parse(data)
#        except TypeError:
#            return None
#        # print(time)
#        return time;

class FirebaseDB(AbstractDB):
    def __init__(self, config):
        super().__init__(config)
        print(self.config)
        if 'FIREBASE' in self.config:
            cred = credentials.Certificate("event-extraction-162da-firebase-adminsdk-f3e3q-1b54b55406.json")
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