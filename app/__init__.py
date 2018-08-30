from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from app import backend

# Initialise the app
app = Flask(__name__)

# Enable Cross Origin Resource Sharing
CORS(app)

# Register backends
api = Api(app)
api.add_resource(backend.Hello, '/api')


if __name__ == '__main__':
    app.run(debug=True)