from rest_framework import serializers

from .models import *


class SpecialistSerializer(serializers.ModelSerializer):
    def get_image(self, specialist):
        return specialist.image.url.replace("minio", "localhost", 1)

    class Meta:
        model = Specialist
        fields = "__all__"


class LectureSerializer(serializers.ModelSerializer):
    specialists = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, lecture):
        return lecture.owner.username

    def get_moderator(self, lecture):
        if lecture.moderator:
            return lecture.moderator.username
            
    def get_specialists(self, lecture):
        items = SpecialistLecture.objects.filter(lecture=lecture)
        return [{**SpecialistSerializer(item.specialist).data, "value": item.value} for item in items]

    class Meta:
        model = Lecture
        fields = '__all__'


class LecturesSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, lecture):
        return lecture.owner.username

    def get_moderator(self, lecture):
        if lecture.moderator:
            return lecture.moderator.username

    class Meta:
        model = Lecture
        fields = "__all__"


class SpecialistLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistLecture
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'date_joined', 'password', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
