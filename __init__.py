import os
import configparser
from pymongo import MongoClient 

try:
    mongo_host = os.environ['MONGO']['HOST']
    mongo_port = int(os.environ['MONGO']['PORT'])
except KeyError:
    configFile = 'config.ini'
    config = configparser.ConfigParser()
    config.read(configFile)
    mongo_host = config['MONGO']['HOST']
    mongo_port = int(config['MONGO']['PORT'])
    
client = MongoClient(mongo_host, mongo_port)
