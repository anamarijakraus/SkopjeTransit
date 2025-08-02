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
]