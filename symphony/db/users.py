import secrets

from symphony import utils


def insert_track_ratings(client, cursor, user_id):
    tracks_per_time = [('long_term', 20), ('medium_term', 30),
                       ('short_term', 40)]

    for time_frame, limit in tracks_per_time:
        response = client.current_user_top_tracks(time_range=time_frame,
                                                  limit=limit)
        utils.tracks.add_tracks(client, cursor, response['items'], user_id,
                                ratings=True)


def key_exists(cursor, key):
    cursor.execute('SELECT 1 FROM users WHERE api_key = %s', (key,))
    return cursor.fetchone()


def get_api_key(cursor):
    api_key = secrets.token_urlsafe(32)
    while key_exists(cursor, api_key):
        api_key = secrets.token_urlsafe(32)
    return api_key


def add_user(conn, client, user_data):
    cursor = conn.cursor()

    # Fill in missing user data
    api_key = get_api_key(cursor)
    if user_data['images']:
        profile_picture = user_data['images'][0]['url']
    else:
        profile_picture = 'https://i.imgur.com/FteILMO.png'

    # Insert user into database
    cursor.execute(
        """
        INSERT INTO users(
            id,
            api_key,
            name,
            profile_picture
        )
        VALUES(%s, %s, %s, %s)
        """,
        (user_data['id'], api_key, user_data['display_name'], profile_picture)
    )
    conn.commit()

    # Populate user track ratings
    insert_track_ratings(client, cursor, user_data['id'])
    conn.commit()


def update_user(conn, client, user_data):
    cursor = conn.cursor()

    # Delete old user ratings from database
    cursor.execute(
        """
        DELETE FROM ratings
        WHERE ratings.user_id = %s
        """,
        (user_data['id'],)
    )
    conn.commit()

    # Populate user track ratings
    insert_track_ratings(client, cursor, user_data['id'])
    conn.commit()


def user_exists(conn, by, value):
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE %s = %s', (by, value,))
    return cursor.fetchone()