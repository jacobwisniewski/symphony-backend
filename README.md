# Symphony Flask Backend

## How to start development version of Flask API
Start by cd-ing to symphony-backend directory
- Windows Systems:
    ```
    set FLASK_APP=app
    set FLASK_ENV=development
    set DATABASE_URL=
    set CLIENT_ID=
    set CLIENT_SECRET=
    set FRONTEND_URL=
    flask run
    ```
- Unix Systems:
    ```
    export FLASK_APP=app
    export FLASK_ENV=development
    export DATABASE_URL=
    export CLIENT_ID=
    export CLIENT_SECRET=
    export FRONTEND_URL=
    flask run
    ```
### Required Environment Variables
- FLASK_APP: Set to symphony
- FLASK_ENV: development when testing
- DATABASE_URL: MongoDB URL
- CLIENT_ID: Spotify Client ID
- CLIENT_SECRET: Spotify Client Secret
- FRONTEND_URL: The frontend URL, used for callbacks
  - '/profile/callback', '/create/callback' and '/join/callback' should be registered as callback URIs for Spotify

## How to use MongoDB compass (GUI style tool for MongoDB clusters)
Do these steps if you have never used MongoDB compass
1. Download [MongoDB compass](https://www.mongodb.com/download-center?jmp=hero#compass), remember to choose your systems package
2. Install MongoDB compass, follow the prompts given

Once you have MongoDB compass installed follow these steps
1. Go to the [MongoDB website](https://www.mongodb.com/) and log-in using your details 
2. Once you're in the cluster dashboard, select your cluster and click "CONNECT"
3. You'll see a prompt "Connect with MongoDB Compass", click it and on the next prompt choose "I am using Compass 1.12 or later"
4. Click "Copy"
5. Now start MongoDB compass 
6. You'll see that it detected that you have a MongoDB connection string in your clipboard, choose "Yes"
7. Fill in the "Username" and "Password" inputs with your details
8. Connect!
Once you've done this once, your connection will be in your recents. So next time you need to use this, just use your rcent connections.