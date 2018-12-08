import os
import logging

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
import psycopg2

from symphony import endpoints, utils


def create_app():
    """Initialises the Flask Application with extension"""
    app = Flask(__name__)

    # Enable Cross Origin Resource Sharing
    CORS(app)

    # Enable RESTful module
    api = Api(app)

    # Initialise database if it hasn't already been done
    init_db()

    # Create admin credentials if not already done
    utils.load_cache()

    app.logger.setLevel(logging.INFO)

    # Register API Endpoints
    api.add_resource(endpoints.callback.Callback, '/api/callback')
    api.add_resource(endpoints.dashboard.Dashboard, '/api/dash')
    api.add_resource(endpoints.create.Create, '/api/create')
    api.add_resource(endpoints.join.Join, '/api/join')
    api.add_resource(endpoints.leave.Leave, '/api/leave')
    api.add_resource(endpoints.find.Find, '/api/find')

    return app


def init_db():
    conn = psycopg2.connect(os.environ.get('DB_ARGS'))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT EXISTS(
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public');
        """
    )
    db_exists = cursor.fetchone()[0]
    if not db_exists:
        from symphony.db import init_db
        init_db.create_db(conn)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app = create_app()
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=False)
