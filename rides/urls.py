from django.urls import path
from . import views

app_name = 'rides'
urlpatterns = [
    path('create/', views.create_ride, name='create'),
    path('<int:ride_id>/book/', views.book_ride, name='book'),
]