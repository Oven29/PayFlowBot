import random
from string import hexdigits


def generate_rand_string(length: int) -> str:
    "Generate random string"
    return ''.join(random.choice(hexdigits) for _ in range(length))
