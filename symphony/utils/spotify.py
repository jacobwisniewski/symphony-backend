import os
import requests
import time
from symphony.db import Collection
from functools import wraps


class LoginError(BaseException):
    """Exception returned when invalid Spotify Access-Codes are used"""
    pass


def get_tokens(access_code, page):
    """Gets the tokens associated with the access code

    :param access_code: Spotify access code after a user has logged into the
        callback /{page}/callback
    :type access_code: str
    :param page: The page for the front-end to redirect to  after the call,
        must be 'profile', 'create' or 'join'
    :type page: str
    :returns: Dictionary containing keys: 'access_token', 'refresh_token'
        and 'expiry' - the expiry of the access token in POSIX time
    :rtype: dict
    :raises: LoginError if login using :param:access_code fails
    """
    # Make POST request to Spotify API
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': access_code,
            'redirect_uri': os.environ['FRONTEND_URL'] + f'/{page}/callback',
            'client_id': os.environ['CLIENT_ID'],
            'client_secret': os.environ['CLIENT_SECRET']
        }
    )

    if not response.ok:
        raise LoginError('Invalid access code')

    json = response.json()

    # Structure output
    tokens = {
        'access_token': json['access_token'],
        'refresh_token': json['refresh_token'],
        'expiry': time.time() + json['expires_in'],
    }

    return tokens


def get_user_profile(tokens):
    """Gets the Spotify data of a user

    :param tokens: Dictionary containing the user's access token in key
        'access_token'
    :type tokens: dict
    :returns: Dictionary containing user data, 'spotify_id', 'user_name' and
        'profile_picture'. Profile  picture will default to an empty user URL if
        the user doesn't have one associated with Spotify
    :rtype: dict
    """
    access_token = tokens['access_token']
    response = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    # Fill in missing data
    if response['display_name'] is None:
        response['display_name'] = response['id']

    if response['images']:
        profile_picture = response['images'][0]['url']
    else:
        # Blank profile picture for users without one
        profile_picture = 'https://i.imgur.com/FteILMO.png'

    profile = {
        'spotify_id': response['id'],
        'user_name': response['display_name'],
        'profile_picture': profile_picture
    }

    return profile


def get_top_songs(tokens):
    """Gets a user's top 50 songs from the last few weeks

    :param tokens: Dictionary containing the user's access token in key
        'access_token'
    :type tokens: dict
    :returns: List of Spotify track IDs, may be less than 50 songs depending
        on user
    :rtype: list
    """
    access_token = tokens['access_token']
    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': 50, 'time_range': 'short_term'}
    ).json()

    tracks = [track['id'] for track in response['items']]

    return tracks


def get_admin(func):
    """Decorator to return admin MongoDB document

    Decorator inspects current database for the admin user in the admin
    collection. If it exists tokens are updated if they need to be and if it
    does not exist a new document is created for the admin account.
    The first argument of func should be reserved for the admin document.
    """
    @wraps(func)
    def token_updated(*args, **kwargs):
        col = Collection('admin')
        admin = col.find('user', 'admin')
        if admin:
            admin_id = admin['_id']
            expiry = admin['tokens']['expiry']
            now = time.time()
            # Use refresh token if access token is expired
            if now > expiry + 10:
                refresh_token = admin['tokens']['refresh_token']
                tokens = update_tokens(refresh_token)
                tokens['refresh_token'] = refresh_token
                col.update(admin['_id'], {'tokens': tokens})
        else:
            # Source the admin access code from env var
            # Redirect URI should be /create/callback
            access_code = os.environ['ACCESS_CODE']
            tokens = get_tokens(access_code, 'create')
            admin_id = col.insert({'user': 'admin', 'tokens': tokens})

        admin = col[admin_id]
        return func(admin, *args, **kwargs)
    return token_updated


def update_tokens(refresh_token):
    """Updates a user's access and refresh tokens

    :param refresh_token: The refresh token of the user
    :type refresh_token: str
    :returns: Dictionary containing keys: 'access_token', 'refresh_token'
        and 'expiry' - the expiry of the access token in POSIX time
    :rtype: dict
    """
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': os.environ['CLIENT_ID'],
            'client_secret': os.environ['CLIENT_SECRET']
        })
    data = response.json()
    tokens = {
        'access_token': data['access_token'],
        # 'refresh_token': data['refresh_token'],
        'expiry': time.time() + data['expires_in'],
    }
    return tokens


@get_admin
def create_playlist(admin, playlist_name):
    """Creates playlist on Symphony App Spotify account

    Use by calling :func:create_playlist(playlist_name)

    :param admin: Admin document in database, automatically filled by decorator
    :param playlist_name: The name of the Spotify playlist to be created
    :type playlist_name: str
    :returns: Tuple of the playlist id and the playlist URL
    :rtype: tuple
    """
    profile = get_user_profile(admin['tokens'])
    admin_spotify_id = profile['spotify_id']
    access_token = admin['tokens']['access_token']

    response = requests.post(
        f'https://api.spotify.com/v1/users/{admin_spotify_id}/playlists',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'name': playlist_name,
              'description': f'Symphony Playlist for {playlist_name}'})
    data = response.json()
    return data['id'], data['href']
