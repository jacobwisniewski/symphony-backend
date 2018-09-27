from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from symphony.endpoints import callback, profile


def create_app():
    # Initialise the symphony
    app = Flask(__name__)

    # Enable Cross Origin Resource Sharing
    CORS(app)

    # Enable RESTful module
    api = Api(app)

    # Register API Endpoints
    api.add_resource(profile.Profile, '/api/profile')
    api.add_resource(callback.Callback, '/api/<string:page>/callback')

    return app
