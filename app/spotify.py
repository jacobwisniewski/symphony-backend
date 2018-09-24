import os
import requests
import time


class LoginError(BaseException):
    pass


def get_tokens(access_code):
    """Gets the access token, refresh token and expiry date in POSIX time"""
    # Make POST request to Spotify API
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': access_code,
            'redirect_uri': 'localhost:5000/callback',
            'client_id': os.environ['CLIENT_ID'],
            'client_secret': os.environ['CLIENT_SECRET']
        }
    )

    if response.status_code != 200:
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
    if 'display_name' not in response:
        response['display_name'] = response['id']

    profile = {
        'spotify_id': response['id'],
        'user_name': response['display_name'],
        'profile_picture': response['images']['url']
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
