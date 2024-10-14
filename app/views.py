import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_lecture():
    return Lecture.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_specialists(request):
    query = request.GET.get("query", "")

    specialists = Specialist.objects.filter(status=1).filter(name__icontains=query)

    serializer = SpecialistSerializer(specialists, many=True)

    draft_lecture = get_draft_lecture()

    resp = {
        "specialists": serializer.data,
        "specialists_count": len(serializer.data),
        "draft_lecture": draft_lecture.pk if draft_lecture else None
    }

    return Response(resp)


@api_view(["GET"])
def get_specialist_by_id(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)
    serializer = SpecialistSerializer(specialist, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_specialist(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)

    image = request.data.get("image")
    if image is not None:
        specialist.image = image
        specialist.save()

    serializer = SpecialistSerializer(specialist, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_specialist(request):
    Specialist.objects.create()

    specialists = Specialist.objects.filter(status=1)
    serializer = SpecialistSerializer(specialists, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_specialist(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)
    specialist.status = 2
    specialist.save()

    specialists = Specialist.objects.filter(status=1)
    serializer = SpecialistSerializer(specialists, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_specialist_to_lecture(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)

    draft_lecture = get_draft_lecture()

    if draft_lecture is None:
        draft_lecture = Lecture.objects.create()
        draft_lecture.owner = get_user()
        draft_lecture.date_created = timezone.now()
        draft_lecture.save()

    if SpecialistLecture.objects.filter(lecture=draft_lecture, specialist=specialist).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    item = SpecialistLecture.objects.create()
    item.lecture = draft_lecture
    item.specialist = specialist
    item.save()

    serializer = LectureSerializer(draft_lecture, many=False)

    return Response(serializer.data["specialists"])


@api_view(["POST"])
def update_specialist_image(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)

    image = request.data.get("image")
    if image is not None:
        specialist.image = image
        specialist.save()

    serializer = SpecialistSerializer(specialist)

    return Response(serializer.data)


@api_view(["GET"])
def search_lectures(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    lectures = Lecture.objects.exclude(status__in=[1, 5])

    if status > 0:
        lectures = lectures.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        lectures = lectures.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        lectures = lectures.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = LecturesSerializer(lectures, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_lecture_by_id(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)
    serializer = LectureSerializer(lecture, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_lecture(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)
    serializer = LectureSerializer(lecture, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)

    if lecture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture.status = 2
    lecture.date_formation = timezone.now()
    lecture.save()

    serializer = LectureSerializer(lecture, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture = Lecture.objects.get(pk=lecture_id)

    if lecture.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture.date_complete = timezone.now()
    lecture.status = request_status
    lecture.moderator = get_moderator()
    lecture.save()

    serializer = LectureSerializer(lecture, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_lecture(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)

    if lecture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture.status = 5
    lecture.save()

    serializer = LectureSerializer(lecture, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_specialist_from_lecture(request, lecture_id, specialist_id):
    if not SpecialistLecture.objects.filter(lecture_id=lecture_id, specialist_id=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SpecialistLecture.objects.get(lecture_id=lecture_id, specialist_id=specialist_id)
    item.delete()

    lecture = Lecture.objects.get(pk=lecture_id)

    serializer = LectureSerializer(lecture, many=False)
    specialists = serializer.data["specialists"]

    if len(specialists) == 0:
        lecture.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(specialists)


@api_view(["PUT"])
def update_specialist_in_lecture(request, lecture_id, specialist_id):
    if not SpecialistLecture.objects.filter(specialist_id=specialist_id, lecture_id=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SpecialistLecture.objects.get(specialist_id=specialist_id, lecture_id=lecture_id)

    serializer = SpecialistLectureSerializer(item, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, many=False, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)