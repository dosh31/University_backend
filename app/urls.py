from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('specialists/<int:specialist_id>/', specialist),
    path('lectures/<int:lecture_id>/', lecture),
]