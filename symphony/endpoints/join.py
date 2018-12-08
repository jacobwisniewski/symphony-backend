import os

from flask import current_app, abort
from flask_restful import Resource, reqparse
import psycopg2
import spotipy

from symphony import utils, db

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('api_key', type=str, required=True, default=None,
                    help='API key is required')
parser.add_argument('invite_code', type=str, required=True,
                    help='Invite code is required')


class Join(Resource):
    def post(self):
        args = parser.parse_args()

        # Set up database connection
        conn = psycopg2.connect(os.environ.get('DB_ARGS'))
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Uses provided credentials to get a user from the database
        api_key = args['api_key']
        cursor.execute('SELECT * FROM users WHERE api_key = %s', (api_key, ))
        user = cursor.fetchone()

        if not user:
            abort(401, 'Invalid credentials')

        # Get the corresponding gig
        gig = db.gigs.find_gig(cursor, args['invite_code'])

        # Check that the invite code was valid
        if not gig:
            abort(400, 'Invalid invite code')

        # Check if user is already in the gig
        if db.gigs.user_in_gig(args['invite_code'], cursor, user):
            abort(400, 'User is already in this gig')

        # Add user to gig
        cursor.execute(
            """
            INSERT INTO gig_links(user_id, gig_id)
            VALUES (%s, %s)
            """,
            (user['id'], args['invite_code'])
        )

        # Get the recommendations for the gig
        tracks = utils.group_recommender.get_tracks(conn, args['invite_code'])

        # Authenticate admin Symphony account
        admin_token = utils.get_admin_token()
        admin = spotipy.Spotify(auth=admin_token)

        # Add recommendations to the playlist
        admin.user_playlist_replace_tracks(os.environ.get('ADMIN_ID'),
                                           gig['playlist_id'],
                                           tracks)

        log_msg = f"User {user['name']} connected to {gig['gig_name']}"
        current_app.logger.info(log_msg)

        return gig
