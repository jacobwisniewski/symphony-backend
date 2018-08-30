from flask_restful import Resource, reqparse


class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('access_code', required=True, type=str,
                            help='Access Code is Required')
        args = parser.parse_args()

        # TODO: Add data to MongoDB here
        """
        Unique ID (MongoDB)
        User id (Spotify, user information request)
        Name (Spotify, user information request)
        Tokens (Spotify, token data request)
            Access Token
            Refresh Token
            Expiry Date + Time
        Profile picture URL (Spotify, user information request)
        Top songs (Spotify, user top song request)
        """

        # TODO: Fill in data for response here
        response = {
            'mongo_id': mongo_id,
            'spotify_id': spotify_id,
            'user_name': user_name,
            'profile_picture': profile_picture,
            'user_gigs': user_gigs
        }
        return response
