from rest_framework import serializers

from .models import *


class SpecialistsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, specialist):
        if specialist.image:
            return specialist.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Specialist
        fields = ("id", "name", "status", "image")


class SpecialistSerializer(SpecialistsSerializer):
    class Meta:
        model = Specialist
        fields = "__all__"


class SpecialistAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ("name", "description", "image")


class LecturesSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lecture
        fields = "__all__"


class LectureSerializer(LecturesSerializer):
    specialists = serializers.SerializerMethodField()

    def get_specialists(self, lecture):
        items = SpecialistLecture.objects.filter(lecture=lecture)
        return [SpecialistItemSerializer(item.specialist, context={"comment": item.comment}).data for item in items]


class SpecialistItemSerializer(SpecialistSerializer):
    comment = serializers.SerializerMethodField()

    def get_comment(self, _):
        return self.context.get("comment")

    class Meta:
        model = Specialist
        fields = ("id", "name", "status", "image", "comment")


class SpecialistLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistLecture
        fields = "__all__"


class UpdateLectureStatusAdminSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
