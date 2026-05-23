import uuid

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import SET_NULL

from datetime import date


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False,
                          default=uuid.uuid4, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    bio = models.TextField(blank=True)
    birthdate = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
    )

    # Email notification preferences — opt-out model (True by default)
    # Covers events the user upvoted OR committed to attend.
    email_status_updates = models.BooleanField(
        default=True,
        help_text="Receive emails when events you upvoted or committed to change status.",
    )
    # Covers events the user committed to with an AttendanceCommitment.
    email_event_reminders = models.BooleanField(
        default=True,
        help_text="Receive reminder emails 24 hours before events you committed to attend.",
    )

    # experience =  # A tagging system for capturing various skills someone might have
    # phone number =
    # following = models.ForeignKey("User", on_delete=SET_NULL, null=True)
    # followers =
    # level =  # Capturing what "level" someone is for access and assistance across the site

    USERNAME_FIELD = 'email'
    # Adding fields here also adds them during the createsuperuser command
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return f"{self.first_name} {self.last_name[0]}"

    def get_absolute_url(self):
        return reverse("account_profile", kwargs={"slug": self.username})

    def get_age(self):
        today = date.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
