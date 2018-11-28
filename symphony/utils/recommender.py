from sklearn import tree
from psycopg2.extras import execute_batch
import pandas as pd


def get_user_data(connection, username):
    df = pd.read_sql_query(
        """
        SELECT t.popularity, t.tempo, t.valence, t.liveness, t.energy,
        t.danceability, t.acousticness, r.rating
        FROM tracks t
        INNER JOIN ratings r
        ON t.id = r.track_id
        WHERE r.user_id = %s
        """,
        connection,
        params=(username, )
    )
    return df


def train_model(df):
    # Train decision tree model
    targets = df['rating']
    features = df[[col for col in df.columns if col != 'rating']]
    tree_model = tree.DecisionTreeRegressor(min_samples_leaf=3)
    tree_model.fit(features, targets)
    return tree_model


def get_prediction_data(user_id, row):
    data = {
        'user_id': user_id,
        'track_id': row[0],
        'rating': row[1],
    }
    return data


def predict_tracks(connection, username, model):
    # Gets all tracks the user hasn't listened to recently
    df = pd.read_sql_query(
        """
        SELECT DISTINCT t.name, t.id, t.popularity, t.tempo, t.valence,
        t.liveness, t.energy, t.danceability, t.acousticness
        FROM tracks t
        LEFT JOIN ratings r ON r.track_id = t.id
        WHERE NOT EXISTS 
              (
              SELECT *
              FROM ratings r2
              WHERE r2.user_id = %s AND r2.track_id = t.id AND imputed = 0
              )
        """,
        connection,
        params=(username, )
    )

    # Predicts user ratings for tracks user hasn't listened to
    df['prediction'] = model.predict(df.iloc[:, 2:])

    # Insert the imputed results into the database
    subset = df[['id', 'prediction']]
    data = [get_prediction_data(username, row) for row in subset.values]
    curs = connection.cursor()
    execute_batch(
        curs,
        """
        INSERT INTO ratings(user_id, track_id, rating, imputed)
        VALUES(%(user_id)s, %(track_id)s, %(rating)s, 1)
        ON CONFLICT (user_id, track_id)
            DO UPDATE
            SET rating = %(rating)s,
                imputed = 1
        """,
        data
    )
