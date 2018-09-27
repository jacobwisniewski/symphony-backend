from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from symphony.db import spotify_user
from symphony.utils import spotify


# Parser for /api/profile
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('access_code', required=True, type=str,
                    help='Access code is required')


class Profile(Resource):
    def post(self):
        args = parser.parse_args()
        access_code = args['access_code']

        try:
            tokens = spotify.get_tokens(access_code, 'profile')
        except spotify.LoginError:
            return make_response(
                jsonify({'message': 'Invalid credentials'}), 401
            )

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
        return response
