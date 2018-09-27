import random
import string


def random_string(length):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for char in range(length))
