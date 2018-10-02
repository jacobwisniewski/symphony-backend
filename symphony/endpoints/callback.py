import os
from flask_restful import Resource
from urllib.parse import urlencode
from symphony.utils import random_string


class Callback(Resource):
    def get(self, page):
        """GET /api/callback Returns a Spotify callback URL and state

        :returns: Callback URL with required scopes and randomised state
        :rtype: dict
        """
        redirect_uri = os.environ['FRONTEND_URL'] + f'/{page}/callback'
        state = random_string(16)
        base_url = 'https://accounts.spotify.com/authorize/?'
        query_params = {
            'client_id': os.environ['CLIENT_ID'],
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': 'user-top-read user-read-private',
            'show_dialog': True,
            'state': state
        }
        encoded_params = urlencode(query_params)
        encoded_url = base_url + encoded_params
        return {'url': encoded_url, 'state': state}
