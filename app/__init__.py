from flask import Flask
import os 

#print config
#Setup app
app = Flask(__name__)
app.config.from_object('config') #Reads the config file located at ../

from app import api