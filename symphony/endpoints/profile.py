from flask import current_app, abort
from flask_restful import Resource, reqparse
from spotipy import oauth2
import spotipy
from symphony import config
from symphony.db import users
import psycopg2
from psycopg2 import extras


# Parser for /api/profile
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('access_code', type=str, default=None)
parser.add_argument('api_key', type=str, default=None)


def get_user_data(args):
    # Set up database connection
    conn = psycopg2.connect(config.DB_ARGS)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Get the api_key for the user
    if args['access_code']:
        # Add/update user in database
        auth = oauth2.SpotifyOAuth(
            config.CLIENT_ID,
            config.CLIENT_SECRET,
            redirect_uri=f'{config.FRONTEND_URL}/profile/callback',
            scope='user-library-read,user-top-read'
        )
        tokens = auth.get_access_token(args['access_code'])
        if not tokens:
            return None

        client = spotipy.client.Spotify(tokens['access_token'])
        current_user = client.current_user()
        key = users.add_user(cursor, client, current_user)
    else:
        key = args['api_key']

    # Get user details
    cursor.execute(
        """
        SELECT
            users.api_key,
            users.id as spotify_id,
            users.name,
            users.profile_picture
        FROM users
        WHERE api_key = %s
        """,
        (key, )
    )
    user = cursor.fetchone()

    # Get gig details for gigs the user is in
    cursor.execute(
        """
        SELECT
            gigs.invite_code,
            gigs.name,
            gigs.playlist_url,
            gigs.playlist_id,
            gigs.private,
            gigs.latitude,
            gigs.longitude,
            users.name as owner_name
        FROM gigs
        INNER JOIN gig_links
        ON gigs.invite_code = gig_links.gig_id
        INNER JOIN users
        ON gigs.owner_id = users.id
        WHERE gig_links.user_id = %s
        """,
        (user['spotify_id'],)
    )
    user['gigs'] = cursor.fetchall()

    conn.commit()
    conn.close()

    return user


class Profile(Resource):
    def post(self):
        args = parser.parse_args()

        # Checks that either access code or User ID are provided
        if not args['access_code'] and not args['api_key']:
            abort(400, 'Access code or API key required')
            return

        try:
            user = get_user_data(args)
        except spotipy.oauth2.SpotifyOauthError:
            abort(401, 'Invalid credentials')
            return

        if not user:
            abort(401, 'Invalid credentials')
            return

        log_msg = f"User {user['name']} has viewed their profile"
        current_app.logger.info(log_msg)

        return user
