from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('switch/', views.switch_role, name='switch_role'),
    path('join-community/', views.join_community, name='join_community'),
    path('profile/', views.profile_view, name='profile'),
    path('ride-history/', views.ride_history_view, name='ride_history'),
    path('confirm-ride/<int:booking_id>/', views.confirm_ride, name='confirm_ride'),
    path('start-ride/<int:booking_id>/', views.start_ride, name='start_ride'),
    path('end-ride/<int:booking_id>/', views.end_ride, name='end_ride'),
    path('submit-review/<int:booking_id>/', views.submit_review, name='submit_review'),
    path('top-up-balance/', views.top_up_balance, name='top_up_balance'),
]