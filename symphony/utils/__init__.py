import random
import string


def random_string(length):
    """Generates a random string of set length"""
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for char in range(length))
