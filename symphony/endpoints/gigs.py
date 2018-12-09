import os

from flask import abort
from flask_restful import Resource, reqparse
import psycopg2

from symphony import db

parser = reqparse.RequestParser()
parser.add_argument('api_key', type=str, required=True)


class Gigs(Resource):
    def post(self):
        args = parser.parse_args()
        api_key = args['api_key']

        conn = psycopg2.connect(os.environ.get('DB_ARGS'),
                                cursor_factory=psycopg2.extras.RealDictCursor)
        cursor = conn.cursor()

        user = db.users.find_user(conn, by='api_key', value=api_key)

        if not user:
            abort(401, 'Invalid credentials')
            return

        gig_info = get_gig_info(cursor, api_key)

        return {'gigs': gig_info}


def get_gig_info(cursor, api_key):
    # Get Spotify user ID using api key
    cursor.execute('SELECT id FROM users WHERE api_key = %s', (api_key,))
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
        (user['id'],)
    )
    gig_info = cursor.fetchall()

    # Convert Decimal objects to Floats for JSON serialising
    for gig in gig_info:
        if gig['latitude'] is not None:
            gig['latitude'] = float(gig['latitude'])
        if gig['longitude'] is not None:
            gig['longitude'] = float(gig['longitude'])

    return gig_info
