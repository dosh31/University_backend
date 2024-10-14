from rest_framework import serializers

from .models import *


class SpecialistSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, specialist):
        return specialist.image.url.replace("minio", "localhost", 1)
        
    class Meta:
        model = Specialist
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


class LecturesSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, lecture):
        return lecture.owner.username

    def get_moderator(self, lecture):
        if lecture.moderator:
            return lecture.moderator.username

        return ""

    class Meta:
        model = Lecture
        fields = "__all__"


class LectureSerializer(serializers.ModelSerializer):
    specialists = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, lecture):
        return lecture.owner.username

    def get_moderator(self, lecture):
        return lecture.moderator.username if lecture.moderator else ""
    
    def get_specialists(self, lecture):
        items = SpecialistLecture.objects.filter(lecture=lecture)
        return [{**SpecialistSerializer(item.specialist).data, "value": item.value} for item in items]
    
    class Meta:
        model = Lecture
        fields = "__all__"


class SpecialistLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistLecture
        fields = "__all__"


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            name=validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)