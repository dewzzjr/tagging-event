# -*- coding: utf-8 -*-
from configparser import ConfigParser
from abc import ABC, abstractmethod

class AbstractDB(ABC):
    
    def __init__(self, config = '../config.ini'):
        self.config = ConfigParser()
        self.config.read(config)
    
    @abstractmethod
    def _check_status(self):
        pass
    
    @abstractmethod
    def getAll(self):
        pass
    
    @abstractmethod
    def getId(self, id):
        pass

    @abstractmethod
    def setTimestamp(self, id):
        pass
    
    @abstractmethod
    def getTimestamp(self, id):
        pass
       
    # data = {'_id':[YOUR_ID],'index':[TAG_INDEX],'tag':[TAG_NAME]}
    @abstractmethod
    def setData(self, data):
        pass
    
    @abstractmethod
    def setType(self, id, type):
        pass
    
    @abstractmethod
    def putData(self, data):
        pass
    
    @abstractmethod
    def removeType(self, id):
        pass