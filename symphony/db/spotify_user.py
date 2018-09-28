from symphony.db import Collection


def create_update(tokens, profile, top_songs):
    """Adds user to the database or updates user details"""
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
