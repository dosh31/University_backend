from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Specialist, Lecture, SpecialistLecture


def index(request):
    specialist_name = request.GET.get("specialist_name", "")
    specialists = Specialist.objects.filter(status=1)

    if specialist_name:
        specialists = specialists.filter(name__icontains=specialist_name)

    draft_lecture = get_draft_lecture()

    context = {
        "specialist_name": specialist_name,
        "specialists": specialists
    }

    if draft_lecture:
        context["specialists_count"] = len(draft_lecture.get_specialists())
        context["draft_lecture"] = draft_lecture

    return render(request, "specialists_page.html", context)


def add_specialist_to_draft_lecture(request, specialist_id):
    specialist = Specialist.objects.get(pk=specialist_id)

    draft_lecture = get_draft_lecture()

    if draft_lecture is None:
        draft_lecture = Lecture.objects.create()
        draft_lecture.owner = get_current_user()
        draft_lecture.date_created = timezone.now()
        draft_lecture.save()

    if SpecialistLecture.objects.filter(lecture=draft_lecture, specialist=specialist).exists():
        return redirect("/")

    item = SpecialistLecture(
        lecture=draft_lecture,
        specialist=specialist
    )
    item.save()

    return redirect("/")


def specialist_details(request, specialist_id):
    context = {
        "specialist": Specialist.objects.get(id=specialist_id)
    }

    return render(request, "specialist_page.html", context)


def delete_lecture(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE lectures SET lesson=5 WHERE id = %s", [lecture_id])

    return redirect("/")


def lecture(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return redirect("/")

    context = {
        "lecture": Lecture.objects.get(id=lecture_id),
    }

    return render(request, "lecture_page.html", context)


def get_draft_lecture():
    return Lecture.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()