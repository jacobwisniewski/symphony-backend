import random
import string
import spotipy.util
from symphony import config


def random_string(length):
    """Generates a random string of set length"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for char in range(length))


def get_admin_token():
    token = spotipy.util.prompt_for_user_token(
        username=config.ADMIN_ID,
        scope='playlist-modify-public,playlist-read-private',
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        redirect_uri=config.REDIRECT_URI
    )
    return token


def find_similar_gigs(cursor, invite_code):
    cursor.execute(
        """
        SELECT
            gigs.name as gig_name,
            gigs.invite_code,
            gigs.owner_name,
            gigs.playlist_url,
            gigs.playlist_id,
        WHERE
            gigs.invite_code = %s
        """,
        (invite_code,)
    )
    similar_gigs = cursor.fetchone()
    return similar_gigs


def user_in_gig(invite_code, cursor, user):
    cursor.execute(
        """
        SELECT EXISTS(
            SELECT 1 FROM gig_links
            WHERE gigs_links.gig_id = %s
                AND gig_links.user_id = %s
        )
        """,
        (invite_code, user['id'])
    )
    return cursor.fetchone()[0]