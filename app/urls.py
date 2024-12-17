from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/specialists/', search_specialists),  # GET
    path('api/specialists/<int:specialist_id>/', get_specialist_by_id),  # GET
    path('api/specialists/<int:specialist_id>/update/', update_specialist),  # PUT
    path('api/specialists/<int:specialist_id>/update_image/', update_specialist_image),  # POST
    path('api/specialists/<int:specialist_id>/delete/', delete_specialist),  # DELETE
    path('api/specialists/create/', create_specialist),  # POST
    path('api/specialists/<int:specialist_id>/add_to_lecture/', add_specialist_to_lecture),  # POST

    # Набор методов для заявок
    path('api/lectures/', search_lectures),  # GET
    path('api/lectures/<int:lecture_id>/', get_lecture_by_id),  # GET
    path('api/lectures/<int:lecture_id>/update/', update_lecture),  # PUT
    path('api/lectures/<int:lecture_id>/update_status_user/', update_status_user),  # PUT
    path('api/lectures/<int:lecture_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/lectures/<int:lecture_id>/delete/', delete_lecture),  # DELETE

    # Набор методов для м-м
    path('api/lectures/<int:lecture_id>/update_specialist/<int:specialist_id>/', update_specialist_in_lecture),  # PUT
    path('api/lectures/<int:lecture_id>/delete_specialist/<int:specialist_id>/', delete_specialist_from_lecture),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
