from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from symphony.db import Collection
from symphony import spotify
from symphony.spotify import LoginError
from symphony.auth_uri import random_string


class Create(Resource):
    def __init__(self):
        api.add_resource(create.Create, '/api/create')

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('access_code', required=True, type=str,
                            help='Access Code is Required')
        parser.add_argument('gig_name', required=True, type=str,
                            help='Gig name is required')
        parser.add_argument('latitude', required=False, type=float)
        parser.add_argument('longitude', required=False, type=float)
        parser.add_argument('private', required=True, type=bool,
                            help='Specify if Gig is private')
        parser.add_argument('algorithm', required=True, type=str,
                            help='Type of algorithm is required')
        args = parser.parse_args()
        access_code = args['access_code']

        try:
            tokens = spotify.get_tokens(access_code)
        except LoginError:
            return make_response(
                jsonify({'message': 'Invalid credentials'}), 401
            )

        # Get user details
        profile = spotify.get_user_profile(tokens)
        top_songs = spotify.get_top_songs(tokens)
        users = Collection('users')
        mongo_id = users[profile['spotify_id']]
        gigs = Collection('gigs')

        invite_code = random_string(6)
        code = gigs.find('Invite Code', invite_code)
        while code:
            invite_code = random_string(6)
            code = gigs.find('Invite Code', invite_code)

        gigs.insert({'MongoID': mongo_id,
                     'Gig Name': args['gig_name'],
                     'Owner': profile['spotify_id'],
                     'Private': args['private'],
                     'Latitude': args['latitude'],
                     'Longitude': args['longitude'],
                     'Algorithm': args['algorithm'],
                     'Invite Code': invite_code
        })

        response = {'Invite Code': invite_code}

        return response