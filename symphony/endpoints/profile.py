from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony.db import spotify_user
from symphony.utils import spotify


# Parser for /api/profile
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('access_code', required=True, type=str,
                    help='Access code is required')


class Profile(Resource):
    def post(self):
        """POST /api/profile Returns a user's Symphony profile

        :returns: JSON response with the user's MongoDB ID, Spotify user ID,
            Spotify display name, profile picture URL and their current
            gigs
        :rtype: dict
        """
        args = parser.parse_args()
        access_code = args['access_code']

        try:
            tokens = spotify.get_tokens(access_code, 'profile')
        except spotify.LoginError:
            abort(401, 'Invalid credentials')
            return

        # Get user details
        profile = spotify.get_user_profile(tokens)
        top_songs = spotify.get_top_songs(tokens)
        # Add user to database
        mongo_id = spotify_user.create_update(tokens, profile, top_songs)

        # API JSON response
        response = {
            'mongo_id': str(mongo_id),
            'spotify_id': profile['spotify_id'],
            'user_name': profile['user_name'],
            'profile_picture': profile['profile_picture'],
            'user_gigs': profile['user_gigs']
        }

        log_msg = f"User {profile['user_name']} has viewed their profile"
        current_app.logger.info(log_msg)

        return response
