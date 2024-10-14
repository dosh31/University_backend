from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Specialist(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="images/default.png")
    description = models.TextField(verbose_name="Описание", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"
        db_table = "specialists"


class Lecture(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='moderator')

    room = models.CharField(verbose_name="Аудитория", blank=True, null=True)
    date = models.DateTimeField(verbose_name="Дата занятия", blank=True, null=True)

    def __str__(self):
        return "Лекция №" + str(self.pk)

    class Meta:
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"
        ordering = ('-date_formation', )
        db_table = "lectures"


class SpecialistLecture(models.Model):
    specialist = models.ForeignKey(Specialist, models.DO_NOTHING, blank=True, null=True)
    lecture = models.ForeignKey(Lecture, models.DO_NOTHING, blank=True, null=True)
    value = models.CharField(verbose_name="Поле м-м", blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "specialist_lecture"
