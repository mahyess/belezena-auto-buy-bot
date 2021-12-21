import random
import string


def generate_password(length=None):
    if length is None:
        length = random.randint(6, 10)
    return (
        random.choice(string.ascii_uppercase)
        + "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
        )
        + random.choice(string.digits)
    )
