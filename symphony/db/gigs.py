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
