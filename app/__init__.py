import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from pymongo import MongoClient
from app import login

# Initialise the app
app = Flask(__name__)

# Enable Cross Origin Resource Sharing
CORS(app)

# Enable RESTful module
api = Api(app)

# Register API Endpoints
api.add_resource(login.Login, '/api/login')

# Connect to MongoDB Atlas
mongo_client = MongoClient(os.environ['DATABASE_URL'])

# Connect to database
db = mongo_client.db
