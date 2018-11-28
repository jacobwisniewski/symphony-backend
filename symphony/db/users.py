import secrets

from symphony import utils


def insert_data(client, cursor, user_id, time_frame, limit):
    response = client.current_user_top_tracks(time_range=time_frame,
                                              limit=limit)
    utils.tracks.add_tracks(client, cursor, response['items'], user_id,
                            ratings=True)


def key_exists(cursor, key):
    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE api_key = %s
        """,
        (key, )
    )
    return cursor.fetchone()


def get_api_key(cursor):
    api_key = secrets.token_urlsafe(32)
    while key_exists(cursor, api_key):
        api_key = secrets.token_urlsafe(32)
    return api_key


def add_user(cursor, client, user):
    # Fill in missing user data
    if user['images']:
        user['profile_picture'] = user['images'][0]['url']
    else:
        user['profile_picture'] = 'https://i.imgur.com/FteILMO.png'

    # Generate a unique api key
    user['key'] = get_api_key(cursor)

    # Insert user into database
    cursor.execute(
        """
        INSERT INTO users(
            id,
            api_key,
            name,
            profile_picture
        )
        VALUES(%(id)s, %(key)s, %(display_name)s, %(profile_picture)s)
        ON CONFLICT (id)
            DO UPDATE
            SET api_key = %(key)s,
                profile_picture = %(profile_picture)s,
                name = %(display_name)s
        """,
        user
    )
    # Scrape listening habits of user
    insert_data(client, cursor, user['id'], 'long_term', 20)
    insert_data(client, cursor, user['id'], 'medium_term', 30)
    insert_data(client, cursor, user['id'], 'short_term', 40)

    return user['key']
