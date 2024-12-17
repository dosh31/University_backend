from django.conf import settings
from django.core.management.base import BaseCommand
from minio import Minio

from .utils import *
from app.models import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_specialists():
    Specialist.objects.create(
        name="Сурдоперевод",
        description="Обеспечение учебного процесса квалифицированными специалистами по сурдопереводу.",
        image="1.png"
    )

    Specialist.objects.create(
        name="Сурдотехника и ТСО",
        description="Настройка и обслуживание ТСО и сурдоакустических систем.",
        image="2.png"
    )

    Specialist.objects.create(
        name="Сурдолог",
        description="Занятия по развитию слухо-речевого восприятия и улучшению коммуникативных навыков.",
        image="3.png"
    )

    Specialist.objects.create(
        name="Психолог",
        description="Консультирование для поддержки психологического состояния и эмоциональной устойчивости.",
        image="4.png"
    )

    Specialist.objects.create(
        name="Тьютор",
        description="Индивидуальное консультирование по техническим дисциплинам.",
        image="5.png"
    )

    Specialist.objects.create(
        name="Логопед",
        description="Сопровождение лиц с особыми образовательными потребностями: развитие речи, улучшение фонетико-фонематических и лексико-грамматических навыков.",
        image="6.png"
    )

    client = Minio(settings.MINIO_ENDPOINT,
                   settings.MINIO_ACCESS_KEY,
                   settings.MINIO_SECRET_KEY,
                   secure=settings.MINIO_USE_HTTPS)

    for i in range(1, 7):
        client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, f'{i}.png', f"app/static/images/{i}.png")

    client.fput_object(settings.MINIO_MEDIA_FILES_BUCKET, 'default.png', "app/static/images/default.png")


def add_lectures():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    specialists = Specialist.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_lecture(status, specialists, owner, moderators)

    add_lecture(1, specialists, users[0], moderators)
    add_lecture(2, specialists, users[0], moderators)
    add_lecture(3, specialists, users[0], moderators)
    add_lecture(4, specialists, users[0], moderators)
    add_lecture(5, specialists, users[0], moderators)


def add_lecture(status, specialists, owner, moderators):
    lecture = Lecture.objects.create()
    lecture.status = status

    if status in [3, 4]:
        lecture.moderator = random.choice(moderators)
        lecture.date_complete = random_date()
        lecture.date_formation = lecture.date_complete - random_timedelta()
        lecture.date_created = lecture.date_formation - random_timedelta()
    else:
        lecture.date_formation = random_date()
        lecture.date_created = lecture.date_formation - random_timedelta()

    if status == 3:
        lecture.room = random.randint(200, 1000)

    lecture.date = random_date()

    lecture.owner = owner

    for specialist in random.sample(list(specialists), 3):
        item = SpecialistLecture(
            lecture=lecture,
            specialist=specialist,
            comment="Важный комментарий"
        )
        item.save()

    lecture.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_specialists()
        add_lectures()
