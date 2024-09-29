from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('specialists/<int:specialist_id>/', specialist_details, name="specialist_details"),
    path('specialists/<int:specialist_id>/add_to_lecture/', add_specialist_to_draft_lecture, name="add_specialist_to_draft_lecture"),
    path('lectures/<int:lecture_id>/delete/', delete_lecture, name="delete_lecture"),
    path('lectures/<int:lecture_id>/', lecture)
]
