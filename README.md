# Symphony Flask Backend
A live version of the app can be found at https://smfy.xyz

## How to start development version of Flask API
```
CLIENT_ID = (Spotify Client ID for app)
CLIENT_SECRET = (Spotify Client Secret for app)
REDIRECT_URI = (Redirect URI for Spotify)
DB_ARGS = 'dbname=dbname user=user password=secret' (Fill with Postgres data)
FRONTEND_URL = (Base URL of the front-end)
ADMIN_ID = (Spotify ID of the admin account)
```

`cd` to `/symphony-backend` directory. *Note: There should be no spaces before and after `=`
in commands, and parameters with spaces should have `"` characters surrounding them.*
- Windows Systems:
    ```
    set FLASK_APP=symphony
    set FLASK_ENV=development
    set CLIENT_ID=(Spotify Client ID for app)
    set CLIENT_SECRET=(Spotify Client Secret for app)
    set DB_ARGS="dbname=dbname user=user password=secret" (Fill with Postgres data)
    set FRONTEND_URL=(Base URL of the front-end)
    set ADMIN_ID=(Spotify ID of the admin account)
    set ADMIN_CACHE=(Contents of .cache-spotifyid file created by Spotipy)
    flask run
    ```
- Unix Systems:
    ```
    export FLASK_APP=symphony
    export FLASK_ENV=development
    export CLIENT_ID=(Spotify Client ID for app)
    export CLIENT_SECRET=(Spotify Client Secret for app)
    export DB_ARGS="dbname=dbname user=user password=secret" (Fill with Postgres data)
    export FRONTEND_URL=(Base URL of the front-end)
    export ADMIN_ID=(Spotify ID of the admin account)
    export ADMIN_CACHE=(Contents of .cache-spotifyid file created by Spotipy)
    flask run
    ```
