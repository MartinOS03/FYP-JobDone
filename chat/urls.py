from django.urls import path
from . import views

# REF-003: Django URL Routing - URL patterns for chat app
urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<str:username>/', views.chat_detail, name='chat_detail'),
    path('<int:chat_id>/job-done/', views.mark_chat_job_done, name='mark_chat_job_done'),
]
