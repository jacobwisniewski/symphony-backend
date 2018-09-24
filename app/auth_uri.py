import os
from flask_restful import Resource
from urllib.parse import urlencode
import random
import string

def random_string(length):
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for char in range(length))

class Callback(Resource):
    def get(self):
        """Gets the URL to push to users for callback authentication

        :returns: Callback URL with required scopes
        """
        base_url = 'https://accounts.spotify.com/authorize/?'
        query_params = {
            'client_id': os.environ['CLIENT_ID'],
            'response_type': 'code',
            'redirect_uri': os.environ['REDIRECT_URI'],
            'scope': 'user-top-read user-read-private',
            'show_dialog': False,
            'state': random_string(16)
        }
        encoded_params = urlencode(query_params)
        encoded_url = base_url + encoded_params
        return {'url': encoded_url}