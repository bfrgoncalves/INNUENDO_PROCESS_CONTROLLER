from flask import Flask

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository

# READ CONFIG FILE
config = {}
execfile("config.py", config)

obo = config["obo"]
localNSpace = config["localNSpace"]
protocolsTypes = config["protocolsTypes"]
processTypes = config["processTypes"]
processMessages = config["processMessages"]
basedir = config["basedir"]
AG_HOST = config["AG_HOST"]
AG_PORT = config["AG_PORT"]
AG_REPOSITORY = config["AG_REPOSITORY"]
AG_USER = config["AG_USER"]
AG_PASSWORD = config["AG_PASSWORD"]

# Setup app
app = Flask(__name__)
# Reads the config file located at ../
app.config.from_object('config')

# Setup agraph
server = AllegroGraphServer(AG_HOST, AG_PORT, AG_USER, AG_PASSWORD)
# Default rootCatalog
catalog = server.openCatalog()

myRepository = catalog.getRepository(AG_REPOSITORY, Repository.OPEN)
myRepository.initialize()
dbconAg = myRepository.getConnection()
dedicateddbconAg = myRepository.getConnection()

from app import api