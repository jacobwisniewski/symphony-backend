# Symphony Flask Backend

## How to start development version of Flask API
Create a `config.py` file in the `/symphony` directory. It should contain the
following variables:
```
CLIENT_ID = (Spotify Client ID for app)
CLIENT_SECRET = (Spotify Client Secret for app)
REDIRECT_URI = (Redirect URI for Spotify)
DB_ARGS = 'dbname=dbname user=user password=secret' (Fill with Postgres data)
FRONTEND_URL = (Base URL of the front-end)
ADMIN_ID = (Spotify ID of the admin account)
```

`cd` to `/symphony-backend` directory
- Windows Systems:
    ```
    set FLASK_APP=symphony
    set FLASK_ENV=development
    flask run
    ```
- Unix Systems:
    ```
    export FLASK_APP=symphony
    export FLASK_ENV=development
    flask run
    ```