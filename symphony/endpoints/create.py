from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony import utils
from symphony.db import gigs
from symphony.utils import group_recommender, find_similar_gigs
from symphony import config
import psycopg2
from psycopg2 import extras
import spotipy

# Parser for /api/create
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('api_key', type=str, required=True, default=None,
                    help='User ID is required')
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
        conn = psycopg2.connect(config.DB_ARGS)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Uses provided credentials to get a user from the database
        api_key = args['api_key']
        cursor.execute('SELECT * FROM users WHERE api_key = %s', (api_key, ))
        user = cursor.fetchone()

        if not user:
            abort(401, 'Invalid credentials')

        # Picks a unique invite code
        invite_code = utils.random_string(6)
        similar_gigs = find_similar_gigs(cursor, invite_code)
        while similar_gigs:
            invite_code = utils.random_string(6)
            similar_gigs = find_similar_gigs(cursor, invite_code)

        # Create the playlist to insert songs into
        admin_token = utils.get_admin_token()
        admin = spotipy.Spotify(auth=admin_token)
        playlist = admin.user_playlist_create(config.ADMIN_ID,
                                              args['gig_name'])

        # Insert the new gig into the database
        gig_info = {
            'owner_id': user['id'],
            'name': args['gig_name'],
            'playlist_url': playlist['href'],
            'playlist_id': playlist['id'],
            'private': args['private'],
            'latitude': args['latitude'],
            'longitude': args['longitude'],
            'invite_code': invite_code
        }
        gigs.create_gig(conn, gig_info)

        # Get the recommendations for the gig
        tracks = group_recommender.get_gig_recommendations(conn, invite_code)
        # Add recommendations to the playlist
        admin.user_playlist_add_tracks(config.ADMIN_ID,
                                       playlist['id'],
                                       tracks)

        # Generate API response
        response = {
            'gig_name': args['gig_name'],
            'invite_code': invite_code,
            'playlist_url': playlist['href'],
            'playlist_id': playlist['id'],
        }

        log_msg = f"New gig {args['gig_name']} created by {user['user_name']}"
        current_app.logger.info(log_msg)

        return response
