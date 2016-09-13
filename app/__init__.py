from flask import Flask
import os 

#Setup app
app = Flask(__name__)
app.config.from_object('config') #Reads the config file located at ../

from app import api