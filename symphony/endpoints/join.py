from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony.db import Collection, spotify_user

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('mongo_id', type=str, required=True, default=None,
                    help='Mongo ID is required')
parser.add_argument('invite_code', type=str, required=True,
                    help='Invite code is required')


class Join(Resource):
    def post(self):
        args = parser.parse_args()

        users = Collection('users')
        user = users[args['mongo_id']]

        if not user:
            abort(401, 'Invalid credentials')

        gigs = Collection('gigs')
        gig = gigs.find('invite_code', args['invite_code'])

        if not gig:
            abort(400, 'Invalid invite code')

        if args['mongo_id'] in gig['users']:
            abort(405, 'User is already in this gig')

        gig_info = {'gig_name': gig['gig_name'],
                    'gig_id': str(gig['_id']),
                    'owner_name': gig['owner_name'],
                    'playlist_url': gig['playlist_url'],
                    'invite_code': gig['invite_code']}
        spotify_user.update_user(gig_info, gig['playlist_url'], user)

        response = {'playlist_url': gig['playlist_url'],
                    'playlist_id': gig['playlist_id'],
                    'gig_name': gig['gig_name'],
                    'owner_name': gig['owner_name']}

        log_msg = f"User {user['user_name']} connected to {gig['gig_name']}"
        current_app.logger.info(log_msg)

        return response
