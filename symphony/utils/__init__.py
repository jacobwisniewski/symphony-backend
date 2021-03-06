import os
import random
import string

from spotipy import util

from . import recommender, group_recommender, tracks

__all__ = ['recommender', 'group_recommender', 'tracks']


def random_string(length):
    """Generates a random string of set length"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for char in range(length))


def get_admin_token():
    token = util.prompt_for_user_token(
        username=os.environ.get('ADMIN_ID'),
        scope='playlist-modify-public',
        client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'),
        redirect_uri=f"{os.environ.get('FRONTEND_URL')}/callback"
    )
    return token


def load_cache():
    admin_id = os.environ.get('ADMIN_ID')
    cache_path = f'.cache-{admin_id}'

    # Populate cache if it doesn't already exist
    if not os.path.isfile(cache_path):
        cache_contents = os.environ.get('ADMIN_CACHE')
        with open(cache_path, 'w') as f:
            f.write(cache_contents)
        print('New cache file created')
