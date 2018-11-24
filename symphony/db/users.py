from symphony.utils import tracks
import secrets


def insert_data(client, cursor, user_id, time_frame, limit):
    response = client.current_user_top_tracks(time_range=time_frame,
                                              limit=limit)
    tracks.add_tracks(client, cursor, response['items'], user_id, ratings=True)


def key_exists(cursor, key):
    cursor.execute(
        """
        SELECT gigs.api_key
        FROM gigs
        WHERE api_key = %s
        """,
        key
    )
    return cursor.fetchone()[0]


def get_api_key(cursor):
    api_key = secrets.token_urlsafe(32)
    while key_exists(cursor, api_key):
        api_key = secrets.token_urlsafe(32)
    return api_key


def add_user(cursor, client, user, tokens):
    # Fill in missing user data
    if 'images' in user:
        profile_picture = user['images'][0]['url']
    else:
        profile_picture = 'https://i.imgur.com/FteILMO.png'

    # Generate a unique api key
    api_key = get_api_key(cursor)

    # Insert user into database
    cursor.execute(
        """
        INSERT INTO users(
            id,
            api_key,
            name,
            profile_picture,
            access_token,
            token_type,
            expires_in,
            refresh_token,
            scope,
            expires_at
        )
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id)
            DO NOTHING
        """,
        (
            user['id'],
            api_key,
            user['display_name'],
            profile_picture,
            tokens['access_token'],
            tokens['token_type'],
            tokens['expires_in'],
            tokens['refresh_token'],
            tokens['scope'],
            tokens['expires_at']
        )
    )
    # Scrape listening habits of user
    insert_data(client, cursor, user['id'], 'long_term', 20)
    insert_data(client, cursor, user['id'], 'medium_term', 30)
    insert_data(client, cursor, user['id'], 'short_term', 40)
