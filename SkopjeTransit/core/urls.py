from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('scam-safety/', views.scam_safety_view, name='scam_safety'),
]

