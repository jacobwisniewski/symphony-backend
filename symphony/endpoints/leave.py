from flask import abort
from flask_restful import Resource, reqparse
from symphony.utils import group_recommender, find_similar_gigs, user_in_gig
import psycopg2
from psycopg2 import extras
from symphony import config, utils
import spotipy


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('api_key', type=str, required=True, default=None,
                    help='API Key is required')
parser.add_argument('invite_code', type=str, required=True,
                    help='Invite code is required')


class Leave(Resource):
    def post(self):
        args = parser.parse_args()

        # Set up database connection
        conn = psycopg2.connect(config.DB_ARGS)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Uses provided credentials to get a user from the database
        api_key = args['api_key']
        cursor.execute('SELECT * FROM users WHERE api_key = %s', (api_key,))
        user = cursor.fetchone()

        if not user:
            abort(401, 'Invalid credentials')

        # Get the corresponding gig
        gig = find_similar_gigs(cursor, args['invite_code'])

        # Check that the invite code was valid
        if not gig:
            abort(400, 'Invalid invite code')

        # Check if user is already in the gig
        if not user_in_gig(args['invite_code'], cursor, user):
            abort(405, 'User is not in this gig')

        # Add user to gig
        cursor.execute(
            """
            DELETE FROM gig_links
            WHERE user_id = %s AND gig_id = %s
            """,
            (user['id'], args['invite_code'])
        )

        # Get the recommendations for the gig
        tracks = group_recommender.get_gig_recommendations(conn,
                                                           args['invite_code'])

        # Authenticate admin Symphony account
        admin_token = utils.get_admin_token()
        admin = spotipy.Spotify(auth=admin_token)

        # Delete old tracks
        items = admin.user_playlist(user, playlist_id=gig['playlist_id'],
                                    fields='tracks')['tracks']['items']
        old_tracks = [item['id'] for item in items]
        admin.user_playlist_remove_all_occurrences_of_tracks(
            config.ADMIN_ID, gig['playlist_id'], old_tracks)

        # Add recommendations to the playlist
        admin.user_playlist_add_tracks(config.ADMIN_ID,
                                       gig['playlist_id'],
                                       tracks)

        return {'message': 'Gig successfully left'}
