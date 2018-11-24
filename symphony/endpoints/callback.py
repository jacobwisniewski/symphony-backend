from flask_restful import Resource
from symphony.utils import random_string
from symphony import config
from spotipy import oauth2


class Callback(Resource):
    def get(self, page):
        """GET /api/callback Returns a Spotify callback URL and state

        :returns: Callback URL with required scopes and randomised state
        :rtype: dict
        """
        state = random_string(16)
        auth = oauth2.SpotifyOAuth(
            config.CLIENT_ID,
            config.CLIENT_SECRET,
            redirect_uri=f'{config.FRONTEND_URL}/{page}/callback',
            state=state
        )
        authorize_url = auth.get_authorize_url()
        return {'url': authorize_url, 'state': state}
