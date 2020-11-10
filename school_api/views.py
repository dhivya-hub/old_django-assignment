from django.shortcuts import render
from .models import *
from rest_framework_simplejwt.settings import api_settings

from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib import auth
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.generics import RetrieveAPIView
from django.conf import settings
import jwt
from django.contrib.auth import user_logged_in


def home(request):
    students = Student.objects.all()
    context = {'students':students}
    return render(request, 'school_api/home.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_detail(request):
    user = User.objects.get(username=request.user.username)
    student = Student.objects.get(user=user)
    serializer = StudentSerializer(student, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def teacher_update(request, pk):
    teacher = Teacher.objects.get(id=pk)
    data = request.data

    for existing_subject in teacher.subject.all():
        teacher.subject.remove(existing_subject)

    for subjects in data.get('subject', teacher.subject):
        sub = Subject.objects.get(name=subjects)
        teacher.subject.add(sub)

    teacher.save()
    serializer = TeacherSerializer(teacher)

    return Response(serializer.data)


# @api_view(['POST'])
# def teacher_update(request, pk):
#     teacher = Teacher.objects.get(id=pk)
#     serializer = TeacherSerializer(teacher, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)

@api_view(['GET'])
def teacher_detail(request):
    teacher = Teacher.objects.all()
    serializer = TeacherSerializer(teacher, many=True)
    return Response(serializer.data)


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    try:
        username = request.data['username']
        password = request.data['password']

        user = User.objects.get(username=username, password=password)
        if user:
            try:
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {}
                user_details['name'] = user.username
                user_details['token'] = token
                user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a username and a password'}
        return Response(res)


