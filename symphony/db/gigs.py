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


def delete_gig(conn, gig_id):
    curs = conn.cursor()
    curs.execute(
        """
        DELETE FROM gigs
        WHERE id = %s
        """,
        (gig_id, )
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


def get_gigs(conn):
    curs = conn.cursor()
    curs.execute(
        """
        SELECT * FROM gigs
        """
    )
    gigs = curs.fetchall()

    if gigs:
        print('{:>12} {:>12}'.format('id', 'name'))
        for gig in gigs:
            print('{:>12} {:>12}'.format(str(gig[0]), gig[1]))
    else:
        print('There are no gigs available')


if __name__ == '__main__':
    # If running the file directly automatically assign connection to local
    # database
    import psycopg2
    from symphony import config

    connection = psycopg2.connect(config.DB_ARGS)


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
        INNER JOIN gig_links
        ON gigs.invite_code = gig_links.gig_id
        INNER JOIN users
        ON gigs.owner_id = users.id
        WHERE gigs.invite_code = %s
        """,
        (invite_code,)
    )
    gigs = cursor.fetchone()
    return gigs


def user_in_gig(invite_code, cursor, user):
    cursor.execute(
        """
        SELECT EXISTS(
            SELECT 1
            FROM gig_links
            WHERE gig_links.gig_id = %s
                AND gig_links.user_id = %s
        )
        """,
        (invite_code, user['id'])
    )
    response = cursor.fetchone()
    return response['exists']
