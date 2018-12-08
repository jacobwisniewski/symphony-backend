"""
Script to generate the Sqlite3 schema for the database and populate it with
songs
"""
import os

import spotipy
import psycopg2

from symphony import utils


def create_db(conn):
    cursor = conn.cursor()

    # Create schema for track metadata
    cursor.execute(
        """
        CREATE TABLE tracks (
            id            TEXT  NOT NULL  UNIQUE,
            name          TEXT  NOT NULL,
            popularity    REAL  NOT NULL,
            tempo         REAL,
            valence       REAL,
            liveness      REAL,
            energy        REAL,
            danceability  REAL,
            acousticness  REAL,
            PRIMARY KEY(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE artists (
            name      TEXT  NOT NULL,
            id        TEXT  NOT NULL,
            track_id  TEXT  NOT NULL,
            PRIMARY KEY(id, track_id),
            FOREIGN KEY(track_id) REFERENCES tracks(id)
                ON DELETE CASCADE
        )
        """
    )

    # Create schema for users and their song ratings
    cursor.execute(
        """
        CREATE TABLE users (
            id               TEXT     NOT NULL  UNIQUE,
            api_key          TEXT     NOT NULL  UNIQUE,
            name             TEXT     NOT NULL,
            profile_picture  TEXT     NOT NULL,
            PRIMARY KEY(id)
        )        
        """
    )
    cursor.execute(
        """
        CREATE TABLE ratings (
            user_id   TEXT     NOT NULL,
            track_id  TEXT     NOT NULL,
            rating    REAL     NOT NULL  DEFAULT 0.0  CHECK(RATING >= 0.0),
            imputed   INTEGER  NOT NULL  DEFAULT 0,
            PRIMARY KEY(user_id, track_id),
            FOREIGN KEY(user_id)  REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY(track_id) REFERENCES tracks(id)
                ON DELETE CASCADE
        )
        """
    )

    # Create schema for groups of users
    cursor.execute(
        """
        CREATE TABLE gigs (
            invite_code   TEXT     NOT NULL  UNIQUE,
            owner_id      TEXT     NOT NULL,
            name          TEXT     NOT NULL,
            playlist_url  TEXT     NOT NULL,
            playlist_id   TEXT     NOT NULL,
            private       BOOLEAN  NOT NULL  DEFAULT TRUE,
            latitude      NUMERIC,
            longitude     NUMERIC,
            PRIMARY KEY(invite_code),
            FOREIGN KEY(owner_id) REFERENCES users(id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE gig_links (
            user_id  TEXT  NOT NULL,
            gig_id   TEXT  NOT NULL,
            PRIMARY KEY(user_id, gig_id),
            FOREIGN KEY(user_id)  REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY(gig_id) REFERENCES gigs(invite_code)
                ON DELETE CASCADE
        )
        """
    )

    conn.commit()

    # Populate the database with songs from the Global Top 50 playlist
    client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(
        client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET')
    )

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    response = sp.user_playlist_tracks('spotify', '37i9dQZEVXbMDoHDwVN2tF')
    tracks_list = [item['track'] for item in response['items']]
    utils.tracks.add_tracks(sp, cursor, tracks_list)

    conn.commit()


if __name__ == '__main__':
    connection = psycopg2.connect(os.environ.get('DB_ARGS'))
    create_db(connection)
