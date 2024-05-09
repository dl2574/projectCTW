from django.db import models
from django.db.models.deletion import SET_NULL, CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from userProfile.models import User
import uuid


class Event(models.Model):
    class StatusCode(models.TextChoices):
        PROPOSAL = "PR", _("Proposal")
        PLANNING = "PL", _("Planning")
        SCHEDULED = "SC", _("Scheduled")
        COMPLETED = "CO", _("Completed")
        ARCHIVED = "AR", _("Archived")
        DENIED = "DN", _("Denied")
        REMOVED = "RM", _("Removed")
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(User, related_name="up_votes")
    required_num_upvotes = models.PositiveIntegerField(default=3)
    status = models.CharField(max_length=2, choices=StatusCode.choices, default=StatusCode.PROPOSAL)

    def number_of_upvotes(self):
        return self.upvotes.count()
    
    def set_required_num_upvotes(self, num:int):
        if num > 0:
            self.required_num_upvotes = num
            return True
        return False
    
    def user_upvoted(self, user):
        return self.upvotes.filter(id=user.id).exists()
    
    def get_absolute_url(self):
        return reverse("eventDetail", kwargs={"pk": self.pk})

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
