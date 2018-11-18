from symphony.db import Collection


def create_update(tokens, profile, top_songs):
    """Adds user to the database or updates user details

    :param tokens: Dictionary containing the user's access token in key
        'access_token'
    :type tokens: dict
    :param profile: Dictionary with user's Spotify account details, see
        /utils/spotify.py:get_user_profile
    :type profile: dict
    :param top_songs: List of Spotify track IDs of user's top songs, see
        /utils/spotify.py:get_top_songs
    :type top_songs: list
    :returns: MongoID of the user in the database
    :rtype: str
    """
    users = Collection('users')
    user_document = users.find('spotify_id', profile['spotify_id'])
    # Check if user already exists
    if user_document:
        return _update_user(user_document, profile, tokens, top_songs, users)
    else:
        return _create_user(profile, tokens, top_songs, users)


def _update_user(document, profile, tokens, top_songs, users):
    """Updates user data in database"""
    profile['user_gigs'] = document['user_gigs']
    mongo_id = users.update(
        document['_id'],
        {
            'profile_picture': profile['profile_picture'],
            'tokens': tokens,
            'user_name': profile['user_name'],
            'top_songs': top_songs,
        }
    )
    return mongo_id


def _create_user(profile, tokens, top_songs, users):
    """Creates new user in database"""
    profile['user_gigs'] = []
    mongo_id = users.insert({
        'spotify_id': profile['spotify_id'],
        'user_name': profile['user_name'],
        'profile_picture': profile['profile_picture'],
        'tokens': tokens,
        'top_songs': top_songs,
        'user_gigs': profile['user_gigs'],
        'stats': {
            'recommendation_history': [],
            'gig_history': [],
            'past_playlist_urls': []
        }
    })
    return mongo_id


def update_user(gig_info, playlist_url, user):
    """Updates a user's details in the database

    :param gig_info: Information for the gig that the user has joined
    :type gig_info: dict
    :param playlist_url: URL of the playlist the user has created
    :type playlist_url: str
    :param user: The user's current document in the database
    :type user: pymongo.Document
    :returns: None
    """
    # Format data to update for user
    user_gigs, user_stats = user['user_gigs'], user['stats']
    user_gigs.append(gig_info)
    user_stats['gig_history'].append(gig_info)
    user_stats['past_playlist_urls'].append(playlist_url)

    # Update user data
    users = Collection('users')
    users.update(
        user['_id'],
        {
            'user_gigs': user_gigs,
            'stats': user_stats
        })