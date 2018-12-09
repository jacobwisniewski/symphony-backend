"""
Provides a way to easily add list of tracks to the database
"""
from psycopg2.extras import execute_batch


def add_tracks(client, cursor, tracks, user_id=None, ratings=False):
    """Adds a list of tracks to the database

    :param client: A Spotipy client that is authenticated
    :param cursor: Postgres database connection that tracks should be added to
    :param tracks: List of dictionaries with track information to add to the
        database
    :param user_id: The user ID if ratings are being added for a user
    :param ratings: Default False, if True the order of the tracks in the list
        will be added as a ranking for the current user
    :return: None
    """
    if not tracks:
        return None
    execute_batch(
        cursor,
        """
        INSERT INTO tracks(id, name, popularity)
        VALUES(%(id)s, %(name)s, %(popularity)s)
        ON CONFLICT (id)
            DO UPDATE
            SET popularity = %(popularity)s
        """,
        tracks
    )
    add_audio_features(client, cursor, tracks)
    if ratings:
        add_ratings(cursor, tracks, user_id)


def get_ratings_data(user_id, tracks):
    num_tracks = len(tracks)
    data = []
    for rank, track in enumerate(tracks):
        data.append({
            'user_id': user_id,
            'track_id': track['id'],
            'rating': num_tracks - rank
        })
    return data


def add_ratings(cursor, tracks, user_id):
    data = get_ratings_data(user_id, tracks)
    execute_batch(
        cursor,
        """
        INSERT INTO ratings(user_id, track_id, rating)
        VALUES(%(user_id)s, %(track_id)s, %(rating)s)
        ON CONFLICT (user_id, track_id)
            DO UPDATE
            SET rating = %(rating)s
        """,
        data
    )


def get_stats(track):
    return (track['tempo'], track['valence'], track['liveness'],
            track['energy'], track['danceability'], track['acousticness'],
            track['id'])


def add_audio_features(client, cursor, tracks):
    track_ids = [track['id'] for track in tracks]
    response = client.audio_features(tracks=track_ids)
    data = [get_stats(track) for track in response]
    execute_batch(
        cursor,
        """
        UPDATE tracks
        SET tempo = %s,
            valence = %s,
            liveness = %s,
            energy = %s,
            danceability = %s,
            acousticness = %s
        WHERE
            id = %s;
        """,
        data
    )
