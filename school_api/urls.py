from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('student/', student_detail, name='detail'),
    path('teacher_update/<int:pk>/', teacher_update, name='update'),
    path('teacher_detail/', teacher_detail, name='teacher'),
    path('create/', CreateUserAPIView.as_view()),
    path('login/', authenticate_user)
]