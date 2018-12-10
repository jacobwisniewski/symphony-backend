import os


def create_gig(conn, gig_info):
    curs = conn.cursor()
    curs.execute(
        """
        INSERT INTO gigs(
            invite_code,
            owner_id,
            name,
            playlist_url,
            playlist_id,
            private,
            latitude,
            longitude
        )
        VALUES (
            %(invite_code)s,
            %(owner_id)s,
            %(name)s,
            %(playlist_url)s,
            %(playlist_id)s,
            %(private)s,
            %(latitude)s,
            %(longitude)s
        )
        """,
        gig_info
    )
    conn.commit()


def delete_gig(conn, admin, gig):
    # Delete the Gig's playlist from Spotify
    admin.user_playlist_unfollow(os.environ.get('ADMIN_ID'),
                                 gig['playlist_id'])

    # Delete the Gig from the database
    curs = conn.cursor()
    curs.execute(
        """
        DELETE FROM gigs
        WHERE invite_code = %s
        """,
        (gig['invite_code'], )
    )
    conn.commit()


def join_gig(conn, user_id, gig_id):
    curs = conn.cursor()
    curs.execute(
        """
        INSERT INTO gig_links(user_id, gig_id)
        VALUES (%s, %s)
        ON CONFLICT (user_id, gig_id)
            DO NOTHING
        """,
        (user_id, gig_id)
    )
    conn.commit()


def leave_gig(conn, user_id, gig_id):
    curs = conn.cursor()
    curs.execute(
        """
        DELETE FROM gig_links
        WHERE user_id = %s AND gig_id = %s
        """,
        (user_id, gig_id)
    )
    conn.commit()


def find_gig(cursor, invite_code):
    cursor.execute(
        """
        SELECT
            gigs.name as gig_name,
            gigs.invite_code,
            gigs.playlist_url,
            gigs.playlist_id,
            users.name as owner_name
        FROM gigs
        INNER JOIN users
        ON gigs.owner_id = users.id
        WHERE gigs.invite_code = %s
        """,
        (invite_code,)
    )
    gig = cursor.fetchone()
    return gig


def user_in_gig(gig_id, cursor, user):
    cursor.execute(
        """
        SELECT 1
        FROM gig_links
        WHERE gig_links.gig_id = %s AND gig_links.user_id = %s
        """,
        (gig_id, user['id'])
    )
    return cursor.fetchone()


def is_empty(cursor, gig_id):
    cursor.execute(
        """
        SELECT * FROM gig_links
        WHERE gig_links.gig_id = %s
        """,
        (gig_id,)
    )
    response = cursor.fetchone()
    return not response
