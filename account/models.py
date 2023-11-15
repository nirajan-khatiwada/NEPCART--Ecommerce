from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Account(AbstractUser):
    phone_number=models.CharField(max_length=10)
    is_verified=models.BooleanField(default=False)