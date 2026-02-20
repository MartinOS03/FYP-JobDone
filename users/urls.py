from django.urls import path
from . import views

# REF-003: Django URL Routing - path() function and URL patterns
urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    path('register/form/', views.register_page, name='register_page'),
    path('login/form/', views.login_page, name='login_page'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-job/', views.create_job, name='create_job'),
    path('view-requests/', views.view_requests, name='view_requests'),
    path('request-job/<int:job_id>/', views.request_job, name='request_job'),
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('request/<int:request_id>/complete/', views.complete_request, name='complete_request'),
    path('request/<int:request_id>/confirm/', views.confirm_completion, name='confirm_completion'),
    path('request/<int:request_id>/review/', views.submit_review, name='submit_review'),
    path('search-tradesmen/', views.search_tradesmen, name='search_tradesmen'),
    path('post-open-job/', views.post_open_job, name='post_open_job'),
    path('open-jobs-board/', views.open_jobs_board, name='open_jobs_board'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('tradesmen/<int:profile_id>/', views.tradesman_profile_detail, name='tradesman_profile_detail'),
    path('favourites/', views.favourites_list, name='favourites_list'),
    path('favourites/toggle/<int:tradesman_id>/', views.toggle_favourite, name='toggle_favourite'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
