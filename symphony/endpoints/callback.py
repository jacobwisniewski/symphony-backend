import os

from flask_restful import Resource
from spotipy import oauth2

from symphony import utils


class Callback(Resource):
    def get(self):
        """GET /api/callback Returns a Spotify callback URL and state

        :returns: Callback URL with required scopes and randomised state
        :rtype: dict
        """
        state = utils.random_string(16)
        auth = oauth2.SpotifyOAuth(
            os.environ.get('CLIENT_ID'),
            os.environ.get('CLIENT_SECRET'),
            redirect_uri=f"{os.environ.get('FRONTEND_URL')}/callback",
            state=state,
            scope='user-library-read,user-top-read'
        )
        authorize_url = auth.get_authorize_url()
        return {'url': authorize_url, 'state': state}
