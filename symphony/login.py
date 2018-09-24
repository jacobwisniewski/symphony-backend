from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from symphony.db import Collection
from symphony import spotify
from symphony.spotify import LoginError


class Login(Resource):
    def post(self):
        # Parse arguments
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('access_code', required=True, type=str,
                            help='Access Code is Required')
        args = parser.parse_args()
        access_code = args['access_code']

        try:
            tokens = spotify.get_tokens(access_code)
        except LoginError:
            return make_response(
                jsonify({'message': 'Invalid credentials'}), 401
            )

        # Get user details
        profile = spotify.get_user_profile(tokens)
        top_songs = spotify.get_top_songs(tokens)

        # Check if user exists in database
        users = Collection('users')
        document = users.find('spotify_id', profile['spotify_id'])

        if document:
            # Update user data in database
            profile['user_gigs'] = document['user_gigs']
            mongo_id = users.update(
                document['_id'],
                {
                    'profile_picture': profile['profile_picture'],
                    'tokens': tokens,
                    'user_name': profile['user_name'],
                    'top_songs': top_songs,
                }
            )

        else:
            # Create new user in database
            profile['user_gigs'] = []
            mongo_id = users.insert({
                'spotify_id': profile['spotify_id'],
                'user_name': profile['user_name'],
                'profile_picture': profile['profile_picture'],
                'tokens': tokens,
                'top_songs': top_songs,
                'user_gigs': profile['user_gigs'],
                'stats': {
                    'recommendation_history': [],
                    'gig_history': [],
                    'past_gig_urls': []
                }
            })

        # API JSON response
        response = {
            'mongo_id': mongo_id,
            'spotify_id': profile['spotify_id'],
            'user_name': profile['user_name'],
            'profile_picture': profile['profile_picture'],
            'user_gigs': profile['user_gigs']
        }
        return response
