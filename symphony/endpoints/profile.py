from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony.db import spotify_user, Collection
from symphony.utils import spotify


# Parser for /api/profile
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('access_code', type=str, default=None)
parser.add_argument('mongo_id', type=str, default=None)


def get_user(args):
    """Gets the MongoID from user's JSON parameters

    The user is created or updated in the database if an access code was sent
    in the parameters
    :param args: JSON data that was sent to /api/create
    :type args: dict
    :returns: Document of the user in the database
    :rtype: pymongo.Document
    """
    # Get the mongo_id for the user
    if args['access_code']:
        # Add/update user in database
        try:
            tokens = spotify.get_tokens(args['access_code'], 'create')
        except spotify.LoginError:
            # If getting tokens returns an error, return no user
            return None
        profile = spotify.get_user_profile(tokens)
        top_songs = spotify.get_top_songs(tokens)
        mongo_id = spotify_user.create_update(tokens, profile, top_songs)
    else:
        mongo_id = args['mongo_id']

    users = Collection('users')
    return users[mongo_id]


class Profile(Resource):
    def post(self):
        """POST /api/profile Returns a user's Symphony profile

        :returns: JSON response with the user's MongoDB ID, Spotify user ID,
            Spotify display name, profile picture URL and their current
            gigs
        :rtype: dict
        """
        args = parser.parse_args()

        # Checks that either access code or Mongo ID are provided
        if not args['access_code'] and not args['mongo_id']:
            abort(400, 'Invite code or Mongo ID required')
            return

        user = get_user(args)
        if not user:
            abort(401, 'Invalid credentials')
            return

        # API JSON response
        response = {
            'mongo_id': str(user['_id']),
            'spotify_id': user['spotify_id'],
            'user_name': user['user_name'],
            'profile_picture': user['profile_picture'],
            'user_gigs': user['user_gigs']
        }

        log_msg = f"User {user['user_name']} has viewed their profile"
        current_app.logger.info(log_msg)

        return response
