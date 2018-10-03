from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from symphony.endpoints import callback, profile, create, join


def create_app():
    """Initialises the Flask Application with extension"""
    app = Flask(__name__)

    # Enable Cross Origin Resource Sharing
    CORS(app)

    # Enable RESTful module
    api = Api(app)

    # Register API Endpoints
    api.add_resource(callback.Callback, '/api/<string:page>/callback')
    api.add_resource(profile.Profile, '/api/profile')
    api.add_resource(create.Create, '/api/create')
    api.add_resource(join.Join, '/api/join')

    return app
