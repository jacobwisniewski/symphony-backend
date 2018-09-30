from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony.db import Collection, spotify_user
from symphony.utils import spotify
from symphony.utils import random_string

# Parser for /api/create
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('access_code', type=str, default=None)
parser.add_argument('mongo_id', type=str, default=None)
parser.add_argument('latitude', type=float, default=None)
parser.add_argument('longitude', type=float, default=None)
parser.add_argument('gig_name', required=True, type=str,
                    help='Gig name is required')
parser.add_argument('private', required=True, type=bool,
                    help='Specify if Gig is private')
parser.add_argument('algorithm', required=True, type=str,
                    help='Type of algorithm is required')


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
        tokens = spotify.get_tokens(args['access_code'], 'create')
        profile = spotify.get_user_profile(tokens)
        top_songs = spotify.get_top_songs(tokens)
        mongo_id = spotify_user.create_update(tokens, profile, top_songs)
    else:
        mongo_id = args['mongo_id']

    users = Collection('users')
    return users[mongo_id]


def update_user(args, playlist_url, user):
    """Updates a user's details in the database

    :param args: Request POST arguments that the user sent
    :type args: dict
    :param playlist_url: URL of the playlist the user has created
    :type playlist_url: str
    :param user: The user's current document in the database
    :type user: pymongo.Document
    :returns: None
    """
    # Format data to update for user
    user_gigs = user['user_gigs']
    user_gigs.append(args['gig_name'])
    user_stats = user['stats']
    user_stats['gig_history'].append(args['gig_name'])
    user_stats['past_playlist_urls'].append(playlist_url)

    # Update user data
    users = Collection('users')
    users.update(
        user['_id'],
        {
            'user_gigs': user_gigs,
            'stats': user_stats
        })


class Create(Resource):
    def post(self):
        """POST /api/create - Creates a gig if given correct parameters

        :returns: JSON with an unique invite code, the created playlist
            Spotify ID, the playlist's URL and the MongoDB ID of the gig
        :rtype: dict
        """
        args = parser.parse_args()

        # Checks that either access code or mongo id were provided
        if not args['access_code'] and not args['mongo_id']:
            abort(400, 'Invite code or Mongo ID required')
            return

        # Uses provided credentials to get a user from the database
        try:
            user = get_user(args)
        except spotify.LoginError:
            abort(401, 'Invalid credentials')
            return

        gigs = Collection('gigs')

        # Picks a unique invite code
        invite_code = random_string(6)
        code = gigs.find('invite_code', invite_code)
        while code:
            invite_code = random_string(6)
            code = gigs.find('invite_code', invite_code)

        playlist_id, playlist_url = spotify.create_playlist(args['gig_name'])

        # TODO: Implement track choosing algorithms and save to playlist
        # tracks = spotify.generate_tracks(args['algorithm'])
        # populate_playlist(playlist_id, tracks)

        gig_id = gigs.insert({
            'owner_mongo_id': str(user['_id']),
            'owner_name': user['user_name'],
            'gig_name': args['gig_name'],
            'playlist_url': playlist_url,
            'playlist_id': playlist_id,
            'users': [str(user['_id'])],
            'private': args['private'],
            'latitude': args['latitude'],
            'longitude': args['longitude'],
            'algorithm': args['algorithm'],
            'invite_code': invite_code
        })

        update_user(args, playlist_url, user)

        response = {'invite_code': invite_code,
                    'playlist_id': playlist_id,
                    'playlist_url': playlist_url,
                    'gig_id': gig_id}

        log_msg = f"New gig {args['gig_name']} created by {user['user_name']}"
        current_app.logger.info(log_msg)

        return response
