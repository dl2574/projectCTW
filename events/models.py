from django.db import models
from django.db.models.deletion import SET_NULL, CASCADE
from userProfile.models import User
import uuid


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(User, related_name="up_votes")

    def number_of_upvotes(self):
        return self.upvotes.count()

    def __str__(self):
        return self.name


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event = models.OneToOneField(Event, on_delete=CASCADE)
    volunteers = models.ManyToManyField(User, related_name="volunteers")
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.event.name


class ProposedDate(models.Model):
    # Allow multiple dates to be propsed and the best date voted on for the plan to happen
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    for_plan = models.ForeignKey(Plan, on_delete=CASCADE)
    date = models.DateField()
    votes = models.ManyToManyField(User, related_name="date_votes")

    def number_of_votes(self):
        return self.votes.count()
