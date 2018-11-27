from flask import current_app, abort
from flask_restful import Resource, reqparse
from symphony import config
import psycopg2
from psycopg2 import extras
from geopy import distance

# Parser for /api/create
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('api_key', type=str, required=True, default=None,
                    help='User ID is required')
parser.add_argument('latitude', type=float, required=True,
                    help='Coordinates are required to find playlists')
parser.add_argument('longitude', type=float, required=True,
                    help='Coordinates are required to find playlists')


class Find(Resource):
    def get(self):
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

        # Query the database for public Gigs that the user isn't already in
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
            INNER JOIN users
            ON gigs.owner_id = users.id
            INNER JOIN gig_links
            ON gig_links.gig_id = gigs.invite_code
            WHERE 
                gigs.private = FALSE
                AND NOT EXISTS (SELECT gig_links.user_id
                FROM gig_links
                WHERE gig_links.user_id = %s
                AND gig_links.gig_id = gigs.invite_code
                )
            """,
            (user['id'], )
        )
        public_gigs = cursor.fetchall()

        # Locate Gigs within 50 metres of the user
        user_location = (args['latitude'], args['longitude'])
        nearby_gigs = []

        for gig in public_gigs:
            gig_location = (gig['latitude'], gig['longitude'])
            if distance.distance(user_location, gig_location).meters < 50:
                # Convert Decimal objects to Floats for JSON serialising
                gig['latitude'] = float(gig['latitude'])
                gig['longitude'] = float(gig['longitude'])
                nearby_gigs.append(gig)

        log_msg = f"User {user['name']} is looking for nearby playlists"
        current_app.logger.info(log_msg)

        return {'gigs': nearby_gigs}
