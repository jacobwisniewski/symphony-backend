from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony.db import Collection
from symphony.db.spotify_user import update_user
from symphony.utils import spotify, random_string

# Parser for /api/create
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('mongo_id', type=str, required=True, default=None,
                    help='Mongo ID is required')
parser.add_argument('latitude', type=float, default=None)
parser.add_argument('longitude', type=float, default=None)
parser.add_argument('gig_name', required=True, type=str,
                    help='Gig name is required')
parser.add_argument('private', required=True, type=bool,
                    help='Specify if Gig is private')
parser.add_argument('algorithm', required=True, type=str,
                    help='Type of algorithm is required')


class Create(Resource):
    def post(self):
        """POST /api/create - Creates a gig if given correct parameters

        :returns: JSON with an unique invite code, the created playlist
            Spotify ID, the playlist's URL and the MongoDB ID of the gig
        :rtype: dict
        """
        args = parser.parse_args()

        # Uses provided credentials to get a user from the database
        users = Collection('users')
        user = users[args['mongo_id']]

        if not user:
            abort(401, 'Invalid credentials')

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

        gig_info = {'gig_name': args['gig_name'],
                    'gig_id': str(gig_id),
                    'owner_name': user['user_name'],
                    'playlist_id': playlist_url,
                    'invite_code': invite_code}
        update_user(gig_info, playlist_url, user)

        response = {'invite_code': invite_code,
                    'playlist_id': playlist_id,
                    'playlist_url': playlist_url,
                    'gig_id': str(gig_id)}

        log_msg = f"New gig {args['gig_name']} created by {user['user_name']}"
        current_app.logger.info(log_msg)

        return response
