from flask import Flask
from flask_cors import CORS
from flask_restful import Api
import psycopg2

from symphony import config, endpoints, utils


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
    utils.get_admin_token()

    # Register API Endpoints
    api.add_resource(endpoints.callback.Callback,
                     '/api/<string:page>/callback')
    api.add_resource(endpoints.profile.Profile, '/api/profile')
    api.add_resource(endpoints.create.Create, '/api/create')
    api.add_resource(endpoints.join.Join, '/api/join')
    api.add_resource(endpoints.leave.Leave, '/api/leave')
    api.add_resource(endpoints.find.Find, '/api/find')

    return app


def init_db():
    conn = psycopg2.connect(config.DB_ARGS)
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
