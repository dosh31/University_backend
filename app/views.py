import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_lecture(request):
    user = identity_user(request)

    if user is None:
        return None

    lecture = Lecture.objects.filter(owner=user).filter(status=1).first()

    return lecture


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'specialist_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_specialists(request):
    specialist_name = request.GET.get("specialist_name", "")

    specialists = Specialist.objects.filter(status=1)

    if specialist_name:
        specialists = specialists.filter(name__icontains=specialist_name)

    serializer = SpecialistsSerializer(specialists, many=True)

    draft_lecture = get_draft_lecture(request)

    resp = {
        "specialists": serializer.data,
        "specialists_count": SpecialistLecture.objects.filter(lecture=draft_lecture).count() if draft_lecture else None,
        "draft_lecture_id": draft_lecture.pk if draft_lecture else None
    }

    return Response(resp)


@api_view(["GET"])
def get_specialist_by_id(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)
    serializer = SpecialistSerializer(specialist)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=SpecialistSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_specialist(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)

    serializer = SpecialistSerializer(specialist, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=SpecialistAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_specialist(request):
    serializer = SpecialistAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Specialist.objects.create(**serializer.validated_data)

    specialists = Specialist.objects.filter(status=1)
    serializer = SpecialistsSerializer(specialists, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_specialist(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)
    specialist.status = 2
    specialist.save()

    specialist = Specialist.objects.filter(status=1)
    serializer = SpecialistSerializer(specialist, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_specialist_to_lecture(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)

    draft_lecture = get_draft_lecture(request)

    if draft_lecture is None:
        draft_lecture = Lecture.objects.create()
        draft_lecture.date_created = timezone.now()
        draft_lecture.owner = identity_user(request)
        draft_lecture.save()

    if SpecialistLecture.objects.filter(lecture=draft_lecture, specialist=specialist).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = SpecialistLecture.objects.create()
    item.lecture = draft_lecture
    item.specialist = specialist
    item.save()

    serializer = LectureSerializer(draft_lecture)
    return Response(serializer.data["specialists"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_specialist_image(request, specialist_id):
    if not Specialist.objects.filter(pk=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    specialist = Specialist.objects.get(pk=specialist_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    specialist.image = image
    specialist.save()

    serializer = SpecialistSerializer(specialist)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_lectures(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    lectures = Lecture.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        lectures = lectures.filter(owner=user)

    if status_id > 0:
        lectures = lectures.filter(status=status_id)

    # Добавим фильтры по дате
    if date_formation_start and date_formation_end:
        if date_formation_start > date_formation_end:
            return Response({'message': 'Ошибка! Невозможно выполнить сортировку, когда "ДО" превышает "ПОСЛЕ"'},
                            status=status.HTTP_400_BAD_REQUEST)
        lectures = lectures.filter(date_formation__gte=date_formation_start, date_formation__lte=date_formation_end)
    elif date_formation_end:
        lectures = lectures.filter(date_formation__gte=date_formation_end)
    elif date_formation_start:
        lectures = lectures.filter(date_formation__lte=date_formation_start)

    # if date_formation_start and parse_datetime(date_formation_start):
    #     lectures = lectures.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    # if date_formation_end and parse_datetime(date_formation_end):
    #     lectures = lectures.filter(date_formation__lte=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = LecturesSerializer(lectures, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lecture_by_id(request, lecture_id):
    user = identity_user(request)

    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)

    if not user.is_superuser and lecture.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = LectureSerializer(lecture)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=LectureSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_lecture(request, lecture_id):
    user = identity_user(request)

    if not Lecture.objects.filter(pk=lecture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)
    serializer = LectureSerializer(lecture, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, lecture_id):
    user = identity_user(request)

    if not Lecture.objects.filter(pk=lecture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)

    if lecture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture.status = 2
    lecture.date_formation = timezone.now()
    lecture.save()

    serializer = LectureSerializer(lecture)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=UpdateLectureStatusAdminSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, lecture_id):
    if not Lecture.objects.filter(pk=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture = Lecture.objects.get(pk=lecture_id)

    if lecture.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        lecture.room = random.randint(200, 1000)

    lecture.status = request_status
    lecture.date_complete = timezone.now()
    lecture.moderator = identity_user(request)
    lecture.save()

    serializer = LectureSerializer(lecture)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_lecture(request, lecture_id):
    user = identity_user(request)

    if not Lecture.objects.filter(pk=lecture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lecture = Lecture.objects.get(pk=lecture_id)

    if lecture.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lecture.status = 5
    lecture.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_specialist_from_lecture(request, lecture_id, specialist_id):
    user = identity_user(request)

    if not Lecture.objects.filter(pk=lecture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not SpecialistLecture.objects.filter(lecture_id=lecture_id, specialist_id=specialist_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SpecialistLecture.objects.get(lecture_id=lecture_id, specialist_id=specialist_id)
    item.delete()

    lecture = Lecture.objects.get(pk=lecture_id)

    serializer = LectureSerializer(lecture)
    specialists = serializer.data["specialists"]

    return Response(specialists)


@swagger_auto_schema(method='PUT', request_body=SpecialistLectureSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_specialist_in_lecture(request, lecture_id, specialist_id):
    user = identity_user(request)

    if not Lecture.objects.filter(pk=lecture_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not SpecialistLecture.objects.filter(specialist_id=specialist_id, lecture_id=lecture_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = SpecialistLecture.objects.get(specialist_id=specialist_id, lecture_id=lecture_id)

    serializer = SpecialistLectureSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
