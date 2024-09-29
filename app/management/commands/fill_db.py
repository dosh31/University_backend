import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta, get_room


def add_users():
    User.objects.create_user("user", "user@user.com", "1234")
    User.objects.create_superuser("root", "root@root.com", "1234")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234")

    print("Пользователи созданы")


def add_specialists():
    Specialist.objects.create(
        name="Сурдоперевод",
        description="Обеспечение учебного процесса квалифицированными специалистами по сурдопереводу.",
        image="images/1.png"
    )

    Specialist.objects.create(
        name="Сурдотехника и ТСО",
        description="Настройка и обслуживание ТСО и сурдоакустических систем.",
        image="images/2.png"
    )

    Specialist.objects.create(
        name="Сурдолог",
        description="Занятия по развитию слухо-речевого восприятия и улучшению коммуникативных навыков.",
        image="images/3.png"
    )

    Specialist.objects.create(
        name="Психолог",
        description="Консультирование для поддержки психологического состояния и эмоциональной устойчивости.",
        image="images/4.png"
    )

    Specialist.objects.create(
        name="Тьютор",
        description="Индивидуальное консультирование по техническим дисциплинам.",
        image="images/5.png"
    )

    Specialist.objects.create(
        name="Логопед",
        description="Сопровождение лиц с особыми образовательными потребностями: развитие речи, улучшение фонетико-фонематических и лексико-грамматических навыков.",
        image="images/6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_lectures():
    users = User.objects.filter(is_superuser=False)
    moderators = User.objects.filter(is_superuser=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    specialists = Specialist.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        add_lecture(status, specialists, users, moderators)

    add_lecture(1, specialists, users, moderators)

    print("Заявки добавлены")


def add_lecture(status, specialists, users, moderators):
    lecture = Lecture.objects.create()
    lecture.status = status

    if lecture.status in [3, 4]:
        lecture.date_complete = random_date()
        lecture.date_formation = lecture.date_complete - random_timedelta()
        lecture.date_created = lecture.date_formation - random_timedelta()
    else:
        lecture.date_formation = random_date()
        lecture.date_created = lecture.date_formation - random_timedelta()

    lecture.owner = random.choice(users)
    lecture.moderator = random.choice(moderators)

    lecture.room = get_room()
    lecture.date = random_date()

    for specialist in random.sample(list(specialists), 3):
        item = SpecialistLecture(
            lecture=lecture,
            specialist=specialist,
            value="Прийти пораньше"
        )
        item.save()

    lecture.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_specialists()
        add_lectures()



















