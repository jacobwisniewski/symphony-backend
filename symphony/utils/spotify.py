import os
import requests
import time
from symphony.db import Collection
from functools import wraps


def update_admin_token(func):
    @wraps(func)
    def token_updated(*args, **kwargs):
        col = Collection('admin')
        admin = col.find('user', 'admin')
        if admin:
            expiry = admin['tokens']['expiry']
            now = time.time()
            # Use refresh token if access token is expired
            if expiry < now:
                tokens = update_tokens(admin['tokens']['refresh_token'])
                col.update(admin['_id'], {'tokens': tokens})
        else:
            # Source the admin access code from env var
            # Redirect URI should be /create/callback
            access_code = os.environ['ACCESS_CODE']
            tokens = get_tokens(access_code, 'create')
            col.insert({'user': 'admin', 'tokens': tokens})
        return func(*args, **kwargs)
    return token_updated


class LoginError(BaseException):
    pass


def get_tokens(access_code, page):
    """Gets the access token, refresh token and expiry date in POSIX time"""
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
        print(response.json())
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
        profile_picture = 'https://imgur.com/a/crZnMzs'

    profile = {
        'spotify_id': response['id'],
        'user_name': response['display_name'],
        'profile_picture': profile_picture
    }

    return profile


def get_top_songs(tokens):
    access_token = tokens['access_token']
    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'limit': 50, 'time_range': 'short_term'}
    ).json()

    tracks = [track['id'] for track in response['items']]

    return tracks


def update_tokens(refresh_token):
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
        'refresh_token': data['refresh_token'],
        'expiry': time.time() + data['expires_in'],
    }
    return tokens


@update_admin_token
def create_playlist(playlist_name):
    col = Collection('admin')
    admin = col.find('user', 'admin')
    profile = get_user_profile(admin['tokens'])
    admin_id = profile['spotify_id']
    access_token = admin['tokens']['access_token']

    response = requests.post(
        f'https://api.spotify.com/v1/users/{admin_id}/playlists',
        headers={'Authorization': f'Bearer {access_token}'},
        json={'name': playlist_name,
              'description': f'Symphony Playlist for {playlist_name}'})
    data = response.json()
    return data['id'], data['href']
