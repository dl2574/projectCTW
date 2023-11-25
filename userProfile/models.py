import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    birthdate = models.DateField(blank=True, null=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
