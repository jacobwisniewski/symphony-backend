from flask import current_app, abort
from flask_restful import Resource, reqparse
import psycopg2
import spotipy

from symphony import config, db


# Parser for /api/dashboard
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('access_code', type=str, default=None)
parser.add_argument('api_key', type=str, default=None)


class Dashboard(Resource):
    def post(self):
        args = parser.parse_args()

        # Checks that either access code or User ID are provided
        if not args['access_code'] and not args['api_key']:
            abort(400, 'Access code or API key required')
            return

        try:
            user = get_user(args)
        except spotipy.oauth2.SpotifyOauthError:
            abort(401, 'Invalid credentials')
            return

        if not user:
            abort(401, 'Invalid credentials')
            return

        log_msg = f"User {user['name']} has viewed their dashboard"
        current_app.logger.info(log_msg)

        return user


def get_user(args):
    # Set up database connection
    conn = psycopg2.connect(config.DB_ARGS,
                            cursor_factory=psycopg2.extras.RealDictCursor)
    if args['api_key']:
        user = get_user_from_db(conn, by='api_key', value=args['api_key'])
        conn.close()
        return user

    # Get the Spotify data of the user
    access_token = get_access_token(args)
    client = spotipy.client.Spotify(access_token)
    user_data = client.current_user()
    spotify_id = user_data['id']

    # Add or update user details
    if user_exists(conn, spotify_id):
        db.users.update_user(conn, client, user_data)
    else:
        db.users.add_user(conn, client, user_data)

    user = get_user_from_db(conn, by='id', value=spotify_id)
    conn.close()
    return user


def get_access_token(args):
    auth = spotipy.oauth2.SpotifyOAuth(
        config.CLIENT_ID,
        config.CLIENT_SECRET,
        redirect_uri=f'{config.FRONTEND_URL}/callback',
        scope='user-library-read,user-top-read'
    )
    # Attempt to get access token with code provided
    tokens = auth.get_access_token(args['access_code'])
    return tokens['access_token']


def user_exists(conn, spotify_id):
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE id = %s', (spotify_id,))
    return cursor.fetchone()


def get_user_from_db(conn, by, value):
    # Get user details
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            users.api_key,
            users.id as spotify_id,
            users.name,
            users.profile_picture
        FROM users
        WHERE %s = %s
        """,
        (by, value)
    )
    user = cursor.fetchone()
    if user:
        user['gigs'] = get_gig_info(cursor, user['spotify_id'])
    return user


def get_gig_info(cursor, spotify_id):
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
        (spotify_id,)
    )
    gig_info = cursor.fetchall()

    # Convert Decimal objects to Floats for JSON serialising
    for gig in gig_info:
        gig['latitude'] = float(gig['latitude'])
        gig['longitude'] = float(gig['longitude'])

    return gig_info
