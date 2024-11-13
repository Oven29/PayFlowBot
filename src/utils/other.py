import random
from string import hexdigits
from fake_useragent import UserAgent


def generate_rand_string(length: int) -> str:
    "Generate random string"
    return ''.join(random.choice(hexdigits) for _ in range(length))


def get_user_agent() -> str:
    "Get random user agent"
    return UserAgent(os=['windows', 'linux'], platforms=['pc']).random
