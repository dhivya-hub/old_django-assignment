from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.settings import api_settings


class UserSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = User
        fields = ('id','username','password')
        extra_kwargs = {'password': {'write_only': True}}


class SubjectSerializer(serializers.ModelSerializer):

    def to_representation(self, value):
        return value.name

    class Meta:
        model = Subject


class TeacherSerializer(serializers.ModelSerializer):
    # subject = serializers.PrimaryKeyRelatedField(many=True,read_only=False,queryset=Subject.objects.all())
    subject = SubjectSerializer(many=True,read_only=False)

    class Meta:
        model = Teacher
        fields = ['id', 'name','subject']
        depth = 1


class StudentSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True, many=True)

    class Meta:
        model = Student
        fields = ['id', 'username', 'teacher']


class UserLoginSerializer(serializers.Serializer):

        username = serializers.CharField(max_length=255)
        password = serializers.CharField(max_length=128, write_only=True)
        token = serializers.CharField(max_length=255, read_only=True)

        def validate(self, data):
            username = data.get("username", None)
            password = data.get("password", None)
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError(
                    'A user with this email and password is not found.'
                )
            try:
                payload = api_settings.JWT_PAYLOAD_HANDLER(user)
                jwt_token = api_settings.JWT_ENCODE_HANDLER(payload)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'User with given email and password does not exists'
                )
            return {
                'username': user.username,
                'token': jwt_token
            }