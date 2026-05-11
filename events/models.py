from django.db import models
from django.db.models.deletion import SET_NULL, CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from userProfile.models import User
from userProfile.services import email_event_status_update
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(User, related_name="up_votes", blank=True)
    required_num_upvotes = models.PositiveIntegerField(default=3)
    status = models.CharField(
        max_length=2, choices=StatusCode.choices, default=StatusCode.PROPOSAL)
    selected_date = models.DateField(null=True, blank=True)
    date_confirmed_by = models.ForeignKey(
        User, on_delete=SET_NULL, null=True, blank=True,
        related_name='confirmed_events'
    )
    date_confirmed_on = models.DateTimeField(null=True, blank=True)

    def number_of_upvotes(self):
        return self.upvotes.count()

    def set_required_num_upvotes(self, num: int):
        if num > 0:
            self.required_num_upvotes = num
            return True
        return False

    def user_upvoted(self, user):
        return self.upvotes.filter(id=user.id).exists()

    def transition_to_planning(self):
        """
        Transition this event from PROPOSAL to PLANNING.
        Creates the associated Plan and notifies all upvoters.
        Returns (success: bool, error: str | None).
        """
        if self.status != self.StatusCode.PROPOSAL:
            return False, "Event must be in PROPOSAL status"
        if self.number_of_upvotes() < self.required_num_upvotes:
            return False, f"Need {self.required_num_upvotes} upvotes to begin planning"

        self.status = self.StatusCode.PLANNING
        self.save()

        Plan.objects.get_or_create(event=self)
        self._notify_planning_started()
        email_event_status_update(self)
        return True, None

    def _notify_planning_started(self):
        """Create in-app notifications for all upvoters."""
        from notifications.models import EventStatusChange
        notifications = [
            EventStatusChange(
                recipient=user,
                source_event=self,
                message=f"'{
                    self.name}' has enough support to move to planning!",
            )
            for user in self.upvotes.all()
        ]
        EventStatusChange.objects.bulk_create(notifications)

    def get_absolute_url(self):
        return reverse("eventDetail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    event = models.OneToOneField(Event, on_delete=CASCADE)
    minimum_volunteers = models.PositiveIntegerField(default=1)
    maximum_volunteers = models.PositiveIntegerField(null=True, blank=True)
    planning_notes = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    open_date_proposals = models.BooleanField(default=False)

    def confirmed_attendees(self):
        """Return users with YES commitments"""
        return User.objects.filter(
            attendance_commitments__plan=self,
            attendance_commitments__status="YES"
        )

    def maybe_attendees(self):
        """Return users with MAYBE commitments"""
        return User.objects.filter(
            attendance_commitments__plan=self,
            attendance_commitments__status="MAYBE"
        )

    def attendance_counts(self):
        """Return dict with counts: {'yes': X, 'maybe': Y, 'no': Z}"""
        yes = self.confirmed_attendees().count()
        maybe = self.maybe_attendees().count()
        no = self.attendance_commitments.filter(status='NO').count()
        return {'yes': yes, 'maybe': maybe, 'no': no}

    def __str__(self):
        return self.event.name


class ProposedDate(models.Model):
    # Allow multiple dates to be propsed and the best
    # date voted on for the plan to happen
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    for_plan = models.ForeignKey(Plan, on_delete=CASCADE)
    date = models.DateField()
    votes = models.ManyToManyField(User, related_name="date_votes")

    def number_of_votes(self):
        return self.votes.count()


class AttendanceCommitment(models.Model):
    class CommitmentStatus(models.TextChoices):
        YES = "YES", _("Attending")
        MAYBE = "MAYBE", _("Maybe Attending")
        NO = "NO", _("Not Attending")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    plan = models.ForeignKey(Plan, on_delete=CASCADE,
                             related_name='attendance_commitments')
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name='attendance_commitments')
    status = models.CharField(max_length=5, choices=CommitmentStatus.choices)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['plan', 'user']

    def __str__(self):
        return f"{self.user} - {self.get_status_display()}"


class Comment(models.Model):
    comment = models.TextField()
    event = models.ForeignKey(Event, on_delete=CASCADE)
    created_by = models.ForeignKey(User, on_delete=CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment[:50]


class SupplyItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    plan = models.ForeignKey(Plan, on_delete=CASCADE,
                             related_name='supply_items')
    name = models.CharField(max_length=200)
    quantity_needed = models.PositiveIntegerField(default=1)
    quantity_committed = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def is_fulfilled(self):
        """Check if enough quantity has been committed"""
        return self.quantity_committed >= self.quantity_needed

    def remaining_needed(self):
        """Calculate remaining quantity needed"""
        return max(0, self.quantity_needed - self.quantity_committed)

    def update_committed_quantity(self):
        """Recalculate total committed quantity from commitments"""
        from django.db.models import Sum
        total = self.commitments.aggregate(total=Sum('quantity'))['total'] or 0
        self.quantity_committed = total
        self.save(update_fields=['quantity_committed'])

    def __str__(self):
        return f"{self.name} ({self.quantity_committed}/{self.quantity_needed})"


class SupplyCommitment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    supply_item = models.ForeignKey(
        SupplyItem, on_delete=CASCADE, related_name='commitments')
    user = models.ForeignKey(User, on_delete=CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['supply_item', 'user']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.supply_item.update_committed_quantity()

    def delete(self, *args, **kwargs):
        supply_item = self.supply_item
        super().delete(*args, **kwargs)
        supply_item.update_committed_quantity()

    def __str__(self):
        return f"{self.user} - {self.supply_item.name} ({self.quantity})"
