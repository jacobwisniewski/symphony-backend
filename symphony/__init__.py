from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from symphony import login, auth_uri


def create_app():
    # Initialise the symphony
    app = Flask(__name__)

    # Enable Cross Origin Resource Sharing
    CORS(app)

    # Enable RESTful module
    api = Api(app)

    # Register API Endpoints
    api.add_resource(login.Login, '/api/login')
    api.add_resource(auth_uri.Callback, '/api/callback')

    return app
