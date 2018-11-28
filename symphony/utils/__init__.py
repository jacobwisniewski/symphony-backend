import random
import string

from spotipy import util

from symphony import config
from . import recommender, group_recommender, tracks

__all__ = ['recommender', 'group_recommender', 'tracks']


def random_string(length):
    """Generates a random string of set length"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for char in range(length))


def get_admin_token():
    token = util.prompt_for_user_token(
        username=config.ADMIN_ID,
        scope='playlist-modify-public',
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        redirect_uri=config.REDIRECT_URI
    )
    return token
