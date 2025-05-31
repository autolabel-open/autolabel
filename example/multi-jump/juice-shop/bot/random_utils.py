import random
import string


def random_string(
    length: int | tuple[int, int] | None = None,
    chars: str = string.ascii_letters + string.digits,
) -> str:
    if not length:
        length = random.randint(10, 50)
    if isinstance(length, tuple):
        length = random.randint(*length)
    return "".join(random.choice(chars) for _ in range(length))


def random_email() -> str:
    return (
        f"{random_string(random.randint(5,15))}@"
        f"{random_string(random.randint(5,15))}.{random.choice(('com','org','cn','edu'))}"
    )
