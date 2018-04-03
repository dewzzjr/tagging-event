import os
import configparser
from pymongo import MongoClient 

configFile = 'config.ini'
config = configparser.ConfigParser()
config.read(configFile )
client = MongoClient(config['MONGO']['HOST'], 
                     int(config['MONGO']['PORT']))