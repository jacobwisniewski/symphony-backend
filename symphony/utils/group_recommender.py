import psycopg2
from symphony.db.gigs import get_gigs
from symphony import config
from symphony.utils import content_based


def get_gig_recommendations(conn, gig_id):
    curs = conn.cursor()

    # Find number of users in the gig
    curs.execute(
        """
        SELECT DISTINCT gig_links.user_id
        FROM gig_links
        WHERE gig_links.gig_id = %s
        """,
        (gig_id, )
    )
    users = curs.fetchall()
    for user in users:
        data = content_based.get_user_data(conn, user)
        model = content_based.train_model(data)
        content_based.predict_tracks(conn, user, model)

    conn.commit()

    num_users = len(users)

    # Get top songs of the users in the gig
    curs.execute(
        """
        SELECT
            tracks.id
        FROM ratings
        INNER JOIN tracks    ON tracks.id = ratings.track_id
        INNER JOIN gig_links ON gig_links.user_id = ratings.user_id
        WHERE gig_links.gig_id = %s
        GROUP BY tracks.id, tracks.name
        ORDER BY AVG(ratings.rating) DESC
        """,
        (gig_id, )
    )

    # Scale number of songs to fetch with number of users
    tracks_to_fetch = 40
    if num_users > 4:
        tracks_to_fetch = num_users * 10

    query_data = curs.fetchmany(tracks_to_fetch)
    tracks = [track_tuple[0] for track_tuple in query_data]
    return tracks


def main():
    conn = psycopg2.connect(config.DB_ARGS)
    get_gigs(conn)
    gig = input('Enter ID of gig to provide recommendations for: ')
    get_gig_recommendations(conn, gig)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
