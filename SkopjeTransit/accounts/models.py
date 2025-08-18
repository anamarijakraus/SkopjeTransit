from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class User(AbstractUser):
    is_driver = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=True)

    def switch_role(self):
        self.is_driver = not self.is_driver
        self.is_passenger = not self.is_passenger
        self.save()



class Profile(models.Model):
    ROLE_CHOICES = [
        ('passenger', 'Passenger'),
        ('driver', 'Driver'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='passenger')
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
