import random
from datetime import datetime, timedelta
from django.utils import timezone


def random_date():
    now = datetime.now(tz=timezone.utc)
    return now + timedelta(random.uniform(-1, 0) * 100)


def random_timedelta(factor=100):
    return timedelta(random.uniform(0, 1) * factor)


def get_room():
    number = random.randint(0, 831) + 200

    if number > 700:
        return f"{number}л"

    if number < 400 and random.randint(0, 10) < 3:
        return f"{number}э"

    return str(number) + random.choice(['ю', ''])