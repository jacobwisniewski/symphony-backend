import os

from flask import current_app, abort
from flask_restful import Resource, reqparse
import psycopg2
import spotipy

from symphony import utils, db

# Parser for /api/create
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('api_key', type=str, required=True, default=None,
                    help='API key is required')
parser.add_argument('latitude', type=float, default=None)
parser.add_argument('longitude', type=float, default=None)
parser.add_argument('gig_name', required=True, type=str,
                    help='Gig name is required')
parser.add_argument('private', required=True, type=bool,
                    help='Specify if Gig is private')


class Create(Resource):
    def post(self):
        args = parser.parse_args()

        # Set up database connection
        conn = psycopg2.connect(os.environ.get('DB_ARGS'))
        cursor = conn.cursor()

        # Uses provided credentials to get a user from the database
        user = db.users.find_user(conn, by='api_key', value=args['api_key'])

        if not user:
            abort(401, 'Invalid credentials')

        if args['private'] is False:
            if args['longitude'] is None or args['latitude'] is None:
                abort(400, 'Public playlists require coordinates')

        if not 0 < len(args['gig_name']) < 33:
            abort(400, 'Gig name must be 1-32 characters long')

        # Picks a unique invite code
        invite_code = get_invite_code(cursor)

        # Create the playlist to insert songs into
        admin_token = utils.get_admin_token()
        admin = spotipy.Spotify(auth=admin_token)
        playlist = admin.user_playlist_create(os.environ.get('ADMIN_ID'),
                                              args['gig_name'])

        # Insert the new gig into the database
        gig_info = get_gig_info(args, invite_code, playlist, user)
        db.gigs.create_gig(conn, gig_info)
        db.gigs.join_gig(conn, user['id'], invite_code)

        # Add recommendations to the playlist
        tracks = utils.group_recommender.get_tracks(conn, invite_code)
        admin.user_playlist_add_tracks(os.environ.get('ADMIN_ID'),
                                       playlist['id'],
                                       tracks)

        response = get_response(args, invite_code, playlist)
        log_msg = [
            f"Gig Name: {args['gig_name']}",
            f"Created By: {user['name']}",
            f"Playlist Link: {playlist['external_urls']['spotify']}"
        ]
        current_app.logger.info(', '.join(log_msg))

        return response


def get_invite_code(cursor):
    invite_code = utils.random_string(6)
    # Ensure no other gig with the same invite_code exists
    while db.gigs.find_gig(cursor, invite_code):
        invite_code = utils.random_string(6)
    return invite_code


def get_gig_info(args, invite_code, playlist, user):
    return {
        'owner_id': user['id'],
        'name': args['gig_name'],
        'playlist_url': playlist['external_urls']['spotify'],
        'playlist_id': playlist['id'],
        'private': args['private'],
        'latitude': args['latitude'],
        'longitude': args['longitude'],
        'invite_code': invite_code
    }


def get_response(args, invite_code, playlist):
    return {
        'gig_name': args['gig_name'],
        'invite_code': invite_code,
        'playlist_url': playlist['external_urls']['spotify'],
        'playlist_id': playlist['id'],
    }
