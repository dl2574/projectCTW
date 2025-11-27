# Fat Models, Thin Views - Implementation Guide

**Philosophy**: Business logic belongs in models, views should orchestrate

---

## Event Planning Features - Fat Model Examples

### Model: Event

```python
class Event(models.Model):
    # ... existing fields ...

    # ============================================
    # PERMISSION/AUTHORIZATION METHODS
    # ============================================

    def can_user_participate_in_planning(self, user):
        """Check if user can participate in planning activities"""
        if not user.is_authenticated:
            return False
        # Only upvoters can participate (can adjust this rule later)
        return self.upvotes.filter(id=user.id).exists()

    def can_user_confirm_date(self, user):
        """Check if user can confirm the event date"""
        return (
            self.created_by == user and
            self.status == self.StatusCode.PLANNING
        )

    # ============================================
    # STATE TRANSITION METHODS
    # ============================================

    def transition_to_planning(self):
        """
        Transition event from PROPOSAL to PLANNING status.
        Auto-creates Plan and sends notifications.
        Returns (success: bool, error_message: str or None)
        """
        if self.status != self.StatusCode.PROPOSAL:
            return False, "Event must be in PROPOSAL status"

        if self.number_of_upvotes() < self.required_num_upvotes:
            return False, f"Need {self.required_num_upvotes} upvotes"

        # Update status
        self.status = self.StatusCode.PLANNING
        self.save()

        # Create Plan (use get_or_create to be safe)
        from events.models import Plan
        plan, created = Plan.objects.get_or_create(event=self)

        # Notify upvoters
        self.notify_planning_started()

        return True, None

    def confirm_date(self, proposed_date, confirmed_by):
        """
        Confirm event date and transition to SCHEDULED.
        Returns (success: bool, error_message: str or None)
        """
        # Validation
        if not self.can_user_confirm_date(confirmed_by):
            return False, "Only event creator can confirm date during planning"

        if not hasattr(self, 'plan'):
            return False, "Event has no plan"

        if proposed_date.for_plan != self.plan:
            return False, "Proposed date doesn't belong to this event"

        # Update event
        self.selected_date = proposed_date.date
        self.status = self.StatusCode.SCHEDULED
        self.date_confirmed_by = confirmed_by
        self.date_confirmed_on = timezone.now()
        self.save()

        # Mark the proposed date as selected (if using that approach)
        # proposed_date.is_selected = True
        # proposed_date.save()

        # Notify participants
        self.notify_date_confirmed()

        return True, None

    # ============================================
    # BUSINESS LOGIC / CALCULATIONS
    # ============================================

    def get_winning_proposed_date(self):
        """Get the proposed date with the most votes"""
        if not hasattr(self, 'plan'):
            return None

        # Use annotate for efficiency
        from django.db.models import Count
        return (
            self.plan.proposeddate_set
            .annotate(vote_count=Count('votes'))
            .order_by('-vote_count')
            .first()
        )

    def get_planning_stats(self):
        """Get summary statistics for planning phase"""
        if not hasattr(self, 'plan'):
            return None

        from events.models import AttendanceCommitment

        stats = {
            'proposed_dates_count': self.plan.proposeddate_set.count(),
            'supply_items_count': self.plan.supply_items.count(),
            'supply_items_fulfilled': self.plan.supply_items.filter(
                quantity_committed__gte=models.F('quantity_needed')
            ).count(),
            'attending_yes': self.plan.attendance_commitments.filter(
                status=AttendanceCommitment.CommitmentStatus.YES
            ).count(),
            'attending_maybe': self.plan.attendance_commitments.filter(
                status=AttendanceCommitment.CommitmentStatus.MAYBE
            ).count(),
            'attending_no': self.plan.attendance_commitments.filter(
                status=AttendanceCommitment.CommitmentStatus.NO
            ).count(),
        }
        return stats

    def is_ready_to_schedule(self):
        """
        Check if event meets minimum requirements to be scheduled.
        Returns (ready: bool, reasons: list of str)
        """
        reasons = []

        if not hasattr(self, 'plan'):
            reasons.append("No plan exists")
            return False, reasons

        # Check for proposed dates
        if self.plan.proposeddate_set.count() == 0:
            reasons.append("No dates have been proposed")

        # Check for minimum attendees (example: at least 1 YES commitment)
        yes_count = self.plan.attendance_commitments.filter(
            status=AttendanceCommitment.CommitmentStatus.YES
        ).count()
        if yes_count < 1:
            reasons.append("Need at least 1 confirmed attendee")

        # Add more checks as needed

        return len(reasons) == 0, reasons

    # ============================================
    # NOTIFICATION HELPERS
    # ============================================

    def notify_planning_started(self):
        """Notify all upvoters that planning has started"""
        from notifications.models import EventStatusChange

        for user in self.upvotes.all():
            EventStatusChange.objects.create(
                recipient=user,
                event=self,
                old_status=self.StatusCode.PROPOSAL,
                new_status=self.StatusCode.PLANNING,
                message=f"{self.name} has reached {self.required_num_upvotes} upvotes! Help plan the details."
            )

    def notify_date_confirmed(self):
        """Notify participants that date has been confirmed"""
        from notifications.models import EventStatusChange

        # Notify all upvoters
        for user in self.upvotes.all():
            EventStatusChange.objects.create(
                recipient=user,
                event=self,
                old_status=self.StatusCode.PLANNING,
                new_status=self.StatusCode.SCHEDULED,
                message=f"{self.name} is scheduled for {self.selected_date}!"
            )
```

### Model: ProposedDate

```python
class ProposedDate(models.Model):
    # ... existing fields ...

    def user_has_voted(self, user):
        """Check if user has voted for this date"""
        return self.votes.filter(id=user.id).exists()

    def toggle_vote(self, user):
        """
        Toggle user's vote for this date.
        Returns (voted: bool, message: str)
        """
        if not user.is_authenticated:
            return False, "Must be logged in to vote"

        # Check if user can participate
        if not self.for_plan.event.can_user_participate_in_planning(user):
            return False, "Only event upvoters can vote on dates"

        if self.user_has_voted(user):
            self.votes.remove(user)
            return False, "Vote removed"
        else:
            self.votes.add(user)
            return True, "Vote added"

    @classmethod
    def propose_date(cls, plan, date, proposed_by):
        """
        Create a new proposed date with validation.
        Returns (proposed_date or None, error_message or None)
        """
        from django.utils import timezone
        from datetime import timedelta

        # Validation
        if not proposed_by.is_authenticated:
            return None, "Must be logged in"

        if not plan.event.can_user_participate_in_planning(proposed_by):
            return None, "Only event upvoters can propose dates"

        if plan.event.status != Event.StatusCode.PLANNING:
            return None, "Event must be in planning status"

        # Date must be in future
        if date <= timezone.now().date():
            return None, "Date must be in the future"

        # Date must be at least 7 days in advance (example rule)
        min_date = timezone.now().date() + timedelta(days=7)
        if date < min_date:
            return None, "Event must be at least 7 days in advance"

        # Check if date already proposed
        if cls.objects.filter(for_plan=plan, date=date).exists():
            return None, "This date has already been proposed"

        # Create proposed date
        proposed_date = cls.objects.create(
            for_plan=plan,
            date=date,
            created_by=proposed_by
        )

        # Auto-vote for it
        proposed_date.votes.add(proposed_by)

        return proposed_date, None
```

### Model: SupplyItem

```python
class SupplyItem(models.Model):
    # ... fields ...

    def is_fulfilled(self):
        """Check if enough quantity has been committed"""
        return self.quantity_committed >= self.quantity_needed

    def remaining_needed(self):
        """Calculate remaining quantity needed"""
        return max(0, self.quantity_needed - self.quantity_committed)

    def get_commitments_summary(self):
        """Get list of who's bringing what"""
        return [
            {
                'user': c.user,
                'quantity': c.quantity
            }
            for c in self.commitments.all()
        ]

    def update_committed_quantity(self):
        """Recalculate total committed quantity from commitments"""
        from django.db.models import Sum
        total = self.commitments.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        self.quantity_committed = total
        self.save(update_fields=['quantity_committed'])

    @classmethod
    def add_item(cls, plan, name, quantity_needed, category, added_by):
        """
        Add a supply item with validation.
        Returns (supply_item or None, error_message or None)
        """
        # Validation
        if not added_by.is_authenticated:
            return None, "Must be logged in"

        if not plan.event.can_user_participate_in_planning(added_by):
            return None, "Only event upvoters can add supplies"

        if plan.event.status != Event.StatusCode.PLANNING:
            return None, "Event must be in planning status"

        if quantity_needed < 1:
            return None, "Quantity must be at least 1"

        if len(name.strip()) == 0:
            return None, "Item name is required"

        # Create item
        item = cls.objects.create(
            plan=plan,
            name=name.strip(),
            quantity_needed=quantity_needed,
            category=category,
            created_by=added_by
        )

        return item, None
```

### Model: SupplyCommitment

```python
class SupplyCommitment(models.Model):
    # ... fields ...

    def save(self, *args, **kwargs):
        """Override save to update supply item quantity"""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Update supply item's committed quantity
        self.supply_item.update_committed_quantity()

    def delete(self, *args, **kwargs):
        """Override delete to update supply item quantity"""
        supply_item = self.supply_item
        super().delete(*args, **kwargs)

        # Update supply item's committed quantity
        supply_item.update_committed_quantity()

    @classmethod
    def commit_to_supply(cls, supply_item, user, quantity):
        """
        Create or update supply commitment.
        Returns (commitment or None, error_message or None)
        """
        # Validation
        if not user.is_authenticated:
            return None, "Must be logged in"

        if not supply_item.plan.event.can_user_participate_in_planning(user):
            return None, "Only event upvoters can commit to supplies"

        if quantity < 1:
            return None, "Quantity must be at least 1"

        # Create or update commitment
        commitment, created = cls.objects.update_or_create(
            supply_item=supply_item,
            user=user,
            defaults={'quantity': quantity}
        )

        return commitment, None
```

### Model: AttendanceCommitment

```python
class AttendanceCommitment(models.Model):
    # ... fields ...

    @classmethod
    def set_commitment(cls, plan, user, status):
        """
        Set or update user's attendance commitment.
        Returns (commitment, created: bool)
        """
        if not user.is_authenticated:
            return None, False

        # You might want permission check here
        # if not plan.event.can_user_participate_in_planning(user):
        #     return None, False

        commitment, created = cls.objects.update_or_create(
            plan=plan,
            user=user,
            defaults={'status': status}
        )

        return commitment, created

    def can_user_modify(self, user):
        """Check if user can modify this commitment"""
        return self.user == user
```

### Custom Manager Example

```python
class SupplyItemManager(models.Manager):
    def fulfilled(self):
        """Get all fulfilled supply items"""
        return self.filter(quantity_committed__gte=models.F('quantity_needed'))

    def unfulfilled(self):
        """Get all unfulfilled supply items"""
        return self.filter(quantity_committed__lt=models.F('quantity_needed'))

    def for_event(self, event):
        """Get all supply items for an event"""
        return self.filter(plan__event=event)

class SupplyItem(models.Model):
    # ... fields ...

    objects = SupplyItemManager()
```

---

## Corresponding Thin Views

### View: proposeDate

```python
@login_required
def proposeDateView(request, pk):
    """Propose a new date for event planning"""
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        date_str = request.POST.get('proposed_date')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format")
            return redirect('eventDetail', pk=pk)

        # Call model method - business logic lives there!
        proposed_date, error = ProposedDate.propose_date(
            plan=event.plan,
            date=date,
            proposed_by=request.user
        )

        if error:
            messages.error(request, error)
        else:
            messages.success(request, f"Date {date} proposed successfully!")

    return redirect('eventDetail', pk=pk)
```

### View: voteDate

```python
@login_required
def voteDateView(request, pk, date_id):
    """Toggle vote for a proposed date"""
    proposed_date = get_object_or_404(ProposedDate, pk=date_id)

    # Call model method
    voted, message = proposed_date.toggle_vote(request.user)

    messages.success(request, message)
    return redirect('eventDetail', pk=pk)
```

### View: confirmDate

```python
@login_required
def confirmDateView(request, pk, date_id):
    """Confirm winning date and schedule event"""
    event = get_object_or_404(Event, pk=pk)
    proposed_date = get_object_or_404(ProposedDate, pk=date_id)

    # Call model method - all business logic there!
    success, error = event.confirm_date(proposed_date, request.user)

    if error:
        messages.error(request, error)
    else:
        messages.success(request, f"Event scheduled for {event.selected_date}!")

    return redirect('eventDetail', pk=pk)
```

### View: addSupply

```python
@login_required
def addSupplyView(request, pk):
    """Add supply item to event planning"""
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('item_name', '')
        quantity = int(request.POST.get('quantity', 1))
        category = request.POST.get('category', '')

        # Call model method
        item, error = SupplyItem.add_item(
            plan=event.plan,
            name=name,
            quantity_needed=quantity,
            category=category,
            added_by=request.user
        )

        if error:
            messages.error(request, error)
        else:
            messages.success(request, f"Added {item.name} to supply list")

    return redirect('eventDetail', pk=pk)
```

### View: commitSupply

```python
@login_required
def commitSupplyView(request, pk, supply_id):
    """Commit to bringing a supply item"""
    supply_item = get_object_or_404(SupplyItem, pk=supply_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Call model method
        commitment, error = SupplyCommitment.commit_to_supply(
            supply_item=supply_item,
            user=request.user,
            quantity=quantity
        )

        if error:
            messages.error(request, error)
        else:
            messages.success(request, f"You committed to bring {quantity} {supply_item.name}")

    return redirect('eventDetail', pk=pk)
```

### View: updateAttendance

```python
@login_required
def updateAttendanceView(request, pk):
    """Update user's attendance commitment"""
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')

        # Validate status
        if status not in ['YES', 'MAYBE', 'NO']:
            messages.error(request, "Invalid attendance status")
            return redirect('eventDetail', pk=pk)

        # Call model method
        commitment, created = AttendanceCommitment.set_commitment(
            plan=event.plan,
            user=request.user,
            status=status
        )

        if commitment:
            action = "updated" if not created else "set"
            messages.success(request, f"Attendance {action} to {commitment.get_status_display()}")
        else:
            messages.error(request, "Could not update attendance")

    return redirect('eventDetail', pk=pk)
```

### View: eventDetail (showing how to use model methods)

```python
def eventDetailView(request, pk):
    """Display event details with planning interface if applicable"""
    event = get_object_or_404(Event, pk=pk)

    # Use model methods to prepare context
    context = {
        'event': event,
        'user_upvoted': event.user_upvoted(request.user) if request.user.is_authenticated else False,
    }

    # Planning-specific context
    if event.status == Event.StatusCode.PLANNING:
        context['can_participate'] = event.can_user_participate_in_planning(request.user)
        context['planning_stats'] = event.get_planning_stats()
        context['winning_date'] = event.get_winning_proposed_date()
        context['is_creator'] = event.can_user_confirm_date(request.user)

        # Get user's attendance commitment
        if request.user.is_authenticated:
            try:
                commitment = event.plan.attendance_commitments.get(user=request.user)
                context['user_commitment'] = commitment.status
            except AttendanceCommitment.DoesNotExist:
                context['user_commitment'] = None

    return render(request, 'events/event_detail.html', context)
```

---

## Key Principles

### ✅ DO Put in Models:
- Permission checks (`can_user_do_something()`)
- Validation logic (`is_valid_for_purpose()`)
- State transitions (`transition_to_state()`)
- Calculations (`get_total()`, `calculate_score()`)
- Business rules (`is_ready_to_advance()`)
- Notification logic (`notify_participants()`)
- Complex queries (custom managers)
- Data formatting for common use cases

### ❌ DON'T Put in Models:
- HTTP request/response handling
- Form processing (use forms.py)
- Template rendering
- Redirects
- Session management
- Cookie handling
- Request-specific logic

### 🤔 Gray Areas:
- **Notifications**: I put these in models as helpers, but you could also use Django signals
- **Permissions**: Django has a permission framework, but simple checks can live in models
- **Validation**: Django has form validation, but business rule validation belongs in models

---

## Benefits You'll See

1. **Easier Testing**: Test business logic without dealing with HTTP requests
2. **Reusability**: Use model methods in views, management commands, shell, etc.
3. **Maintainability**: Business logic in one place, not scattered across views
4. **Readability**: Views are short and tell the story clearly
5. **DRY**: Don't repeat permission checks or validation in multiple views

---

## Code Review Checklist

When you show me code, I'll check:
- [ ] Are views simple and focused on orchestration?
- [ ] Is business logic in models, not views?
- [ ] Do model methods have clear names and docstrings?
- [ ] Are permission checks in model methods?
- [ ] Are state transitions handled by model methods?
- [ ] Do methods return useful values (success/error tuples)?
- [ ] Are complex queries in custom managers?
- [ ] Can the model methods be tested without HTTP?

---

## Questions to Ask Yourself

Before writing code in a view, ask:
1. **"Is this business logic?"** → Put it in the model
2. **"Will I need this elsewhere?"** → Put it in the model
3. **"Does this involve HTTP?"** → Keep it in the view
4. **"Is this just glue code?"** → Fine for view

**Good luck! This pattern will make your code much cleaner and more professional.**
