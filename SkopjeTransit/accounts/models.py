from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_driver = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=True)

    def switch_role(self):
        self.is_driver = not self.is_driver
        self.is_passenger = not self.is_passenger
        self.save()