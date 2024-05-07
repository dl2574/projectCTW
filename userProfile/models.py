import uuid

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import SET_NULL

from datetime import date

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    birthdate = models.DateField(blank=True, null=True)
    # experience = 
    # phone number = 
    # following = models.ForeignKey("User", on_delete=SET_NULL, null=True)
    # followers = 
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return f"{self.first_name} {self.last_name[0]}"
    
    def get_absolute_url(self):
        return reverse("account_profile", kwargs={"slug": self.username})
    
    def get_age(self):
        today = date.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
    
