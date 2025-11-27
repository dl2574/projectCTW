# Event Planning Features - Implementation Roadmap

**Target**: Complete the event planning workflow (PROPOSAL → PLANNING → SCHEDULED)
**Status**: Not Started
**Owner**: David

---

## Overview

This feature enables users to collaboratively plan events that have received enough upvotes:
- Propose and vote on execution dates
- Create supply lists and track commitments
- Track attendance commitments (Yes/Maybe/No)
- Transition from PLANNING to SCHEDULED when ready

---

## Database Models

### ✅ Already Exist (Review & Understand)
- `Event` - Core event model with status and upvotes
- `Plan` - OneToOne with Event, has volunteers ManyToMany
- `ProposedDate` - Date proposals with voting system
- `Comment` - Event comments

### 🔨 New Models to Create

#### 1. SupplyItem
**Purpose**: Track individual items needed for the event

```python
class SupplyItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    plan = models.ForeignKey(Plan, on_delete=CASCADE, related_name='supply_items')
    name = models.CharField(max_length=200)  # e.g., "Shovels"
    quantity_needed = models.PositiveIntegerField(default=1)
    quantity_committed = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, blank=True)  # e.g., "Tools", "Food"
    created_by = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def is_fulfilled(self):
        """Check if enough people have committed to bring this item"""
        return self.quantity_committed >= self.quantity_needed

    def __str__(self):
        return f"{self.name} ({self.quantity_committed}/{self.quantity_needed})"
```

**Think About:**
- Should items be free-text or from predefined categories?
- Do you need a description field for details?
- Should there be a "notes" field for special instructions?

#### 2. SupplyCommitment
**Purpose**: Track who committed to bringing which supplies

```python
class SupplyCommitment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    supply_item = models.ForeignKey(SupplyItem, on_delete=CASCADE, related_name='commitments')
    user = models.ForeignKey(User, on_delete=CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['supply_item', 'user']  # One commitment per user per item

    def __str__(self):
        return f"{self.user.username} - {self.supply_item.name} ({self.quantity})"
```

**Think About:**
- Should users be able to commit to multiple items?
- Can they change their commitment quantity?
- Should you track when they fulfill it (bring it to event)?

#### 3. AttendanceCommitment
**Purpose**: Track user attendance status (Yes/Maybe/No)

```python
class AttendanceCommitment(models.Model):
    class CommitmentStatus(models.TextChoices):
        YES = "YES", _("Attending")
        MAYBE = "MAYBE", _("Maybe Attending")
        NO = "NO", _("Not Attending")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    plan = models.ForeignKey(Plan, on_delete=CASCADE, related_name='attendance_commitments')
    user = models.ForeignKey(User, on_delete=CASCADE)
    status = models.CharField(max_length=5, choices=CommitmentStatus.choices)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['plan', 'user']  # One commitment per user per plan

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"
```

**Think About:**
- Should this replace the `Plan.volunteers` field or work alongside it?
- Can users change their status freely?
- Should you track commitment history for accountability?

### 🔄 Potential Model Modifications

#### Event Model
Consider adding:
```python
selected_date = models.DateField(null=True, blank=True)  # Chosen event date
date_confirmed_by = models.ForeignKey(User, on_delete=SET_NULL, null=True, related_name='confirmed_events')
date_confirmed_on = models.DateTimeField(null=True, blank=True)
```

**OR** add to ProposedDate:
```python
is_selected = models.BooleanField(default=False)
```

**Question for You:** Which approach feels cleaner? Event storing the final date, or marking one ProposedDate as selected?

#### Plan Model
Consider adding:
```python
minimum_volunteers = models.PositiveIntegerField(default=1)  # Min attendees needed
maximum_volunteers = models.PositiveIntegerField(null=True, blank=True)  # Max capacity
planning_notes = models.TextField(blank=True)  # General planning discussion
```

**Think About:**
- Do you need min/max volunteer counts?
- Should the Plan automatically create when Event → PLANNING?
- What's the relationship between Plan.volunteers and AttendanceCommitment?

---

## Design Pattern: Fat Models, Thin Views

**IMPORTANT**: This project follows the "Fat Models, Thin Views" methodology.

- ✅ **Business logic goes in models** (validation, permissions, state transitions, calculations)
- ✅ **Views stay thin** (get data, call model methods, return response)
- ✅ See `FAT_MODELS_GUIDE.md` for detailed examples specific to this feature
- ✅ Model methods should return `(success: bool, error: str or None)` tuples
- ✅ All model methods should be easily testable without HTTP

**Before writing code in a view, ask: "Is this business logic?" → If yes, put it in the model!**

---

## Implementation Checklist

### Phase 1: Database Setup ✅
- [ ] Create new models (SupplyItem, SupplyCommitment, AttendanceCommitment)
- [ ] Decide on Event/ProposedDate modification for selected date
- [ ] Consider Plan model enhancements
- [ ] Create migrations: `python manage.py makemigrations`
- [ ] Review migration file - does it look correct?
- [ ] Apply migrations: `python manage.py migrate`
- [ ] Test in Django shell - create sample data for each model
- [ ] Register new models in admin.py for easy testing

**Testing in Shell:**
```python
from events.models import Event, Plan, SupplyItem, SupplyCommitment, AttendanceCommitment
from django.contrib.auth import get_user_model
User = get_user_model()

# Get or create test user and event
user = User.objects.first()
event = Event.objects.filter(status='PL').first()  # Get a planning event

# Test creating supply item
supply = SupplyItem.objects.create(
    plan=event.plan,
    name="Shovels",
    quantity_needed=5,
    created_by=user
)

# Test supply commitment
commitment = SupplyCommitment.objects.create(
    supply_item=supply,
    user=user,
    quantity=2
)

# Verify supply item updates correctly
supply.quantity_committed = sum(c.quantity for c in supply.commitments.all())
supply.save()
print(f"Supply: {supply} - Fulfilled: {supply.is_fulfilled()}")
```

**Guiding Questions:**
- Do your models create without errors?
- Can you access related objects (e.g., `plan.supply_items.all()`)?
- Are the `__str__` methods helpful?
- Do unique_together constraints work as expected?

---

### Phase 2: Auto-Create Plan on Status Change
**Goal**: Automatically create a Plan when Event moves from PROPOSAL → PLANNING

**Where to Implement**: `events/views.py` in the upvote view (or create a signal)

**Option A - In the Upvote View:**
```python
# In upvoteEvent view, after adding upvote:
if event.number_of_upvotes() >= event.required_num_upvotes:
    if event.status == Event.StatusCode.PROPOSAL:
        event.status = Event.StatusCode.PLANNING
        event.save()

        # Create Plan if it doesn't exist
        Plan.objects.get_or_create(event=event)

        # TODO: Send notifications to upvoters
```

**Option B - Using Django Signals (More Advanced):**
Create `events/signals.py` and use a post_save signal to auto-create Plan.

**Think About:**
- When should the Plan be created - immediately when threshold reached, or manually?
- Should all upvoters automatically be added to Plan.volunteers?
- Do you want to notify upvoters when event moves to planning?

**Implementation Steps:**
- [ ] Decide on signal vs view-based approach
- [ ] Implement Plan creation logic
- [ ] Add error handling (what if Plan already exists?)
- [ ] Test by upvoting an event past threshold
- [ ] Verify Plan is created correctly
- [ ] Check that status changes to PLANNING

---

### Phase 3: Planning Interface - Date Voting
**Goal**: Allow users to propose dates and vote on them

**Where**: `templates/events/event_detail.html` (conditional section when status == PLANNING)

**Views to Create/Modify:**
- [ ] `proposeDateView` - Create a new proposed date
- [ ] `voteDateView` - Vote for a proposed date
- [ ] `confirmDateView` - Creator confirms winning date (moves to SCHEDULED)

**URL Patterns:**
```python
# events/urls.py
path('<uuid:pk>/propose-date/', views.proposeDateView, name='proposeDate'),
path('<uuid:pk>/vote-date/<uuid:date_id>/', views.voteDateView, name='voteDate'),
path('<uuid:pk>/confirm-date/<uuid:date_id>/', views.confirmDateView, name='confirmDate'),
```

**Template Section (example structure):**
```html
{% if event.status == 'PL' %}
  <section class="planning-section">
    <h3>Planning: Execution Date</h3>

    <!-- Form to propose new date -->
    <form method="post" action="{% url 'proposeDate' event.id %}">
      {% csrf_token %}
      <input type="date" name="proposed_date" min="{{ today }}">
      <button type="submit">Propose Date</button>
    </form>

    <!-- List of proposed dates with voting -->
    {% for proposed_date in event.plan.proposeddate_set.all %}
      <div class="proposed-date">
        <span>{{ proposed_date.date }}</span>
        <span>{{ proposed_date.number_of_votes }} votes</span>

        {% if user in proposed_date.votes.all %}
          <button disabled>Voted</button>
        {% else %}
          <form method="post" action="{% url 'voteDate' event.id proposed_date.id %}">
            {% csrf_token %}
            <button type="submit">Vote</button>
          </form>
        {% endif %}
      </div>
    {% endfor %}

    <!-- Creator can confirm winning date -->
    {% if user == event.created_by %}
      <button>Confirm Selected Date</button>
    {% endif %}
  </section>
{% endif %}
```

**Implementation Steps:**
- [ ] Add date proposal form to event_detail.html
- [ ] Create proposeDate view (validate date is in future)
- [ ] Create voteDate view (toggle vote like upvote)
- [ ] Display proposed dates with vote counts
- [ ] Add date validation (min days in advance?)
- [ ] Create confirmDate view (event creator only)
- [ ] Add permissions check (only upvoters can propose/vote?)
- [ ] Style the date voting section
- [ ] Test: Can you propose dates?
- [ ] Test: Can you vote on dates?
- [ ] Test: Can creator confirm winning date?

**Validation to Consider:**
- Date must be in the future
- Minimum advance notice (e.g., 7 days minimum)
- Maximum timeframe (e.g., within 1 year)
- User must be authenticated
- Event must be in PLANNING status

**Guiding Questions:**
- Should users be able to propose multiple dates?
- Can users vote for multiple dates or just one?
- Should there be a deadline for date voting?
- What happens to other proposed dates after one is confirmed?

---

### Phase 4: Planning Interface - Supply List
**Goal**: Allow users to propose supplies and commit to bringing them

**Views to Create:**
- [ ] `addSupplyView` - Add a supply item to the list
- [ ] `commitSupplyView` - Commit to bringing a supply item
- [ ] `removeSupplyCommitmentView` - Remove your commitment

**URL Patterns:**
```python
path('<uuid:pk>/add-supply/', views.addSupplyView, name='addSupply'),
path('<uuid:pk>/commit-supply/<uuid:supply_id>/', views.commitSupplyView, name='commitSupply'),
path('<uuid:pk>/remove-supply-commitment/<uuid:commitment_id>/', views.removeSupplyCommitmentView, name='removeSupplyCommitment'),
```

**Template Section (example structure):**
```html
<section class="planning-section">
  <h3>Planning: Supply List</h3>

  <!-- Form to add supply item -->
  <form method="post" action="{% url 'addSupply' event.id %}">
    {% csrf_token %}
    <input type="text" name="item_name" placeholder="Item name">
    <input type="number" name="quantity" min="1" value="1">
    <select name="category">
      <option value="">No category</option>
      <option value="Tools">Tools</option>
      <option value="Materials">Materials</option>
      <option value="Food">Food</option>
    </select>
    <button type="submit">Add Item</button>
  </form>

  <!-- List of supply items -->
  {% for item in event.plan.supply_items.all %}
    <div class="supply-item {% if item.is_fulfilled %}fulfilled{% endif %}">
      <h4>{{ item.name }}</h4>
      <p>Needed: {{ item.quantity_needed }} | Committed: {{ item.quantity_committed }}</p>

      <!-- Show who's bringing it -->
      {% for commitment in item.commitments.all %}
        <span>{{ commitment.user.get_short_name }} ({{ commitment.quantity }})</span>
      {% endfor %}

      <!-- Commit to bring this item -->
      <form method="post" action="{% url 'commitSupply' event.id item.id %}">
        {% csrf_token %}
        <input type="number" name="quantity" min="1" max="{{ item.quantity_needed }}" value="1">
        <button type="submit">I'll Bring This</button>
      </form>
    </div>
  {% endfor %}
</section>
```

**Implementation Steps:**
- [ ] Create addSupply view with validation
- [ ] Create SupplyItem form (or use direct POST validation)
- [ ] Display supply items list
- [ ] Create commitSupply view
- [ ] Update SupplyItem.quantity_committed when commitment added
- [ ] Show who committed to each item
- [ ] Add visual indicator for fulfilled items
- [ ] Allow users to remove their commitments
- [ ] Test: Can you add supplies?
- [ ] Test: Can you commit to supplies?
- [ ] Test: Does quantity_committed update correctly?
- [ ] Test: Is item marked fulfilled when enough committed?

**Business Logic to Consider:**
- Can users commit more than needed? (Allow or block?)
- Should commitments update the item's quantity_committed automatically?
- Can users edit their commitment quantity?
- Should supply item have a "priority" or "required/optional" field?

**Guiding Questions:**
- Should there be predefined categories or free text?
- Can anyone add items or just event creator?
- Should there be item approval process?
- What if multiple people bring the same item?

---

### Phase 5: Planning Interface - Attendance Commitments
**Goal**: Track who's attending (Yes/Maybe/No)

**Views to Create:**
- [ ] `updateAttendanceView` - Set or update attendance commitment

**URL Pattern:**
```python
path('<uuid:pk>/update-attendance/', views.updateAttendanceView, name='updateAttendance'),
```

**Template Section (example structure):**
```html
<section class="planning-section">
  <h3>Planning: Who's Coming?</h3>

  <!-- Attendance commitment form -->
  <form method="post" action="{% url 'updateAttendance' event.id %}">
    {% csrf_token %}
    <label>
      <input type="radio" name="status" value="YES" {% if user_commitment == 'YES' %}checked{% endif %}>
      I'm attending
    </label>
    <label>
      <input type="radio" name="status" value="MAYBE" {% if user_commitment == 'MAYBE' %}checked{% endif %}>
      Maybe attending
    </label>
    <label>
      <input type="radio" name="status" value="NO" {% if user_commitment == 'NO' %}checked{% endif %}>
      Can't attend
    </label>
    <button type="submit">Update</button>
  </form>

  <!-- Attendance summary -->
  <div class="attendance-summary">
    <p>Attending: {{ yes_count }}</p>
    <p>Maybe: {{ maybe_count }}</p>
    <p>Can't Attend: {{ no_count }}</p>
  </div>

  <!-- List of attendees -->
  <div class="attendee-list">
    {% for commitment in event.plan.attendance_commitments.all %}
      {% if commitment.status == 'YES' %}
        <span class="badge badge-success">{{ commitment.user.get_short_name }}</span>
      {% endif %}
    {% endfor %}
  </div>
</section>
```

**Implementation Steps:**
- [ ] Create updateAttendance view
- [ ] Handle create vs update logic (use get_or_create or update_or_create)
- [ ] Pass user's current commitment to template context
- [ ] Calculate and display attendance counts
- [ ] Show list of committed attendees
- [ ] Style attendance badges/indicators
- [ ] Test: Can you set attendance?
- [ ] Test: Can you change attendance?
- [ ] Test: Do counts update correctly?

**Business Logic:**
- [ ] Decide if upvoters are auto-set to "MAYBE" status
- [ ] Can new users (who didn't upvote) commit to attend?
- [ ] Should Plan.volunteers field be updated based on YES commitments?

**Guiding Questions:**
- Should attendance be public or private?
- Can users see who else is attending?
- Should there be a reminder system for "Maybe" users?
- What's the relationship between this and the original upvote?

---

### Phase 6: Status Transition - PLANNING → SCHEDULED
**Goal**: Move event to SCHEDULED status when date is confirmed

**Where to Implement**: `confirmDateView` in events/views.py

**Logic Flow:**
```python
def confirmDateView(request, pk, date_id):
    event = get_object_or_404(Event, pk=pk)
    proposed_date = get_object_or_404(ProposedDate, pk=date_id, for_plan=event.plan)

    # Validation
    if request.user != event.created_by:
        # Only creator can confirm
        messages.error(request, "Only event creator can confirm date")
        return redirect('eventDetail', pk=pk)

    if event.status != Event.StatusCode.PLANNING:
        messages.error(request, "Event must be in planning status")
        return redirect('eventDetail', pk=pk)

    # Update event
    event.selected_date = proposed_date.date  # Or mark proposed_date.is_selected = True
    event.status = Event.StatusCode.SCHEDULED
    event.date_confirmed_by = request.user
    event.date_confirmed_on = timezone.now()
    event.save()

    # TODO: Send notifications to all committed attendees

    messages.success(request, f"Event scheduled for {proposed_date.date}")
    return redirect('eventDetail', pk=pk)
```

**Implementation Steps:**
- [ ] Create confirmDate view
- [ ] Add permission check (creator only)
- [ ] Update Event status to SCHEDULED
- [ ] Store selected date (decide on approach)
- [ ] Add success message
- [ ] Update event_detail.html to show scheduled date
- [ ] Hide planning interface when status == SCHEDULED
- [ ] Test transition workflow
- [ ] Verify date is stored correctly

**Additional Considerations:**
- [ ] Should there be a minimum committed attendees requirement?
- [ ] Should supply list need to be X% fulfilled?
- [ ] Can creator "unschedule" if plans change?

**Guiding Questions:**
- Can the event go back to PLANNING if date needs to change?
- Should other proposed dates be deleted or kept for history?
- What if no one has committed to attend?

---

### Phase 7: Permissions & Access Control

**Questions to Answer:**
- Who can see planning features?
  - Only upvoters?
  - Anyone viewing the event?
  - Authenticated users only?

- Who can propose dates?
  - Any upvoter?
  - Event creator only?
  - Anyone?

- Who can add supply items?
  - Anyone?
  - Event creator only?
  - Needs approval?

- Who can confirm the winning date?
  - Event creator only ✓ (already decided)
  - Upvoters vote?
  - Automatic?

**Implementation Steps:**
- [ ] Add permission checks to all planning views
- [ ] Create permission helper methods on Event model
- [ ] Test permission denials
- [ ] Add appropriate error messages
- [ ] Consider creating custom decorators for common checks

**Example Helper Methods:**
```python
# In Event model
def user_can_participate_in_planning(self, user):
    """Check if user can participate in planning"""
    return self.upvotes.filter(id=user.id).exists()

def user_is_creator(self, user):
    """Check if user created this event"""
    return self.created_by == user
```

---

### Phase 8: Event Detail Page Integration

**Goal**: Conditionally show planning interface based on event status

**Template Structure:**
```html
<!-- templates/events/event_detail.html -->

<!-- Always shown: Basic event info -->
<div class="event-header">...</div>

{% if event.status == 'PR' %}
  <!-- PROPOSAL Status: Show upvote button -->
  <div class="proposal-section">...</div>
{% endif %}

{% if event.status == 'PL' %}
  <!-- PLANNING Status: Show all planning features -->
  <div class="planning-container">
    {% include 'events/partials/date_voting.html' %}
    {% include 'events/partials/supply_list.html' %}
    {% include 'events/partials/attendance_commitment.html' %}
  </div>
{% endif %}

{% if event.status == 'SC' %}
  <!-- SCHEDULED Status: Show final details -->
  <div class="scheduled-section">
    <h3>Event Scheduled!</h3>
    <p>Date: {{ event.selected_date }}</p>
    <p>Confirmed Attendees: {{ event.plan.attendance_commitments.filter(status='YES').count }}</p>
    <!-- Final supply list, attendee list, etc. -->
  </div>
{% endif %}
```

**Implementation Steps:**
- [ ] Review current event_detail.html template
- [ ] Add conditional sections for each status
- [ ] Consider breaking into partial templates for organization
- [ ] Update view to pass additional context (counts, user commitments, etc.)
- [ ] Style each section appropriately
- [ ] Ensure mobile responsiveness
- [ ] Test on different screen sizes

**Context Data Needed:**
```python
# In eventDetail view
context = {
    'event': event,
    'user_upvoted': event.user_upvoted(request.user),
    'user_commitment': None,  # Get from AttendanceCommitment
    'yes_count': event.plan.attendance_commitments.filter(status='YES').count(),
    'maybe_count': event.plan.attendance_commitments.filter(status='MAYBE').count(),
    # etc.
}
```

---

### Phase 9: Notifications (Basic)

**Goal**: Notify upvoters when event moves to PLANNING status

**Approaches:**
- **Option A**: Use existing notification models (EventStatusChange)
- **Option B**: Email notifications (if configured)
- **Option C**: Both

**Implementation Steps:**
- [ ] Review notifications/models.py
- [ ] Create notifications when status changes to PLANNING
- [ ] Create notifications when date is confirmed (SCHEDULED)
- [ ] Add notification display to user interface
- [ ] Test notifications are created correctly
- [ ] Mark notifications as read functionality

**Example:**
```python
# When transitioning to PLANNING
from notifications.models import EventStatusChange

for user in event.upvotes.all():
    EventStatusChange.objects.create(
        recipient=user,
        event=event,
        old_status=Event.StatusCode.PROPOSAL,
        new_status=Event.StatusCode.PLANNING,
        message=f"{event.name} has moved to planning! Help plan the details."
    )
```

**Think About:**
- When should notifications be sent?
- How should users view notifications?
- Email vs in-app notifications?
- Notification preferences?

---

### Phase 10: Testing Strategy

**Model Tests** (`tests/test_models.py`):
- [ ] Test SupplyItem creation and methods
- [ ] Test SupplyItem.is_fulfilled() logic
- [ ] Test SupplyCommitment creation and unique constraint
- [ ] Test AttendanceCommitment creation and update
- [ ] Test Plan auto-creation on status change (if using signals)
- [ ] Test Event status transitions
- [ ] Test ProposedDate voting

**View Tests** (`tests/test_views.py`):
- [ ] Test proposeDate view (authenticated vs anonymous)
- [ ] Test voteDate view (toggle voting)
- [ ] Test confirmDate view (creator only permission)
- [ ] Test addSupply view
- [ ] Test commitSupply view and quantity updates
- [ ] Test updateAttendance view
- [ ] Test eventDetail view context data
- [ ] Test permission denials return correct errors

**Form Tests** (if using Django forms):
- [ ] Test date validation (future dates only)
- [ ] Test supply item form validation
- [ ] Test attendance commitment form

**Integration Tests**:
- [ ] Test complete workflow: PROPOSAL → upvotes → PLANNING → date vote → SCHEDULED
- [ ] Test multiple users interacting with same event
- [ ] Test edge cases (what if creator deletes account?)

**Example Test:**
```python
def test_supply_commitment_updates_quantity(self):
    """Test that adding supply commitment updates item quantity"""
    # Setup
    supply_item = SupplyItem.objects.create(
        plan=self.plan,
        name="Shovels",
        quantity_needed=5,
        quantity_committed=0
    )

    # Create commitment
    commitment = SupplyCommitment.objects.create(
        supply_item=supply_item,
        user=self.user,
        quantity=2
    )

    # Update supply item (you'll need to handle this in view/signal)
    supply_item.quantity_committed = sum(
        c.quantity for c in supply_item.commitments.all()
    )
    supply_item.save()

    # Assert
    supply_item.refresh_from_db()
    self.assertEqual(supply_item.quantity_committed, 2)
    self.assertFalse(supply_item.is_fulfilled())
```

---

## Potential Pitfalls & Questions

### Database Design Questions

1. **Plan.volunteers vs AttendanceCommitment**
   - Should Plan.volunteers be deprecated?
   - Or should it auto-update based on AttendanceCommitment with status=YES?
   - Having both might cause confusion - which is the "source of truth"?

2. **Supply Quantity Updates**
   - Should SupplyItem.quantity_committed update automatically?
   - Use signals, or update in view when commitment created?
   - What if commitment is deleted - does quantity update?

3. **Date Selection Storage**
   - Event.selected_date field vs ProposedDate.is_selected boolean?
   - What if event date needs to change after scheduled?
   - Keep proposed dates for history or delete after selection?

### Permission & Access Control

4. **Who Can Participate in Planning?**
   - Only original upvoters?
   - New users who discover event during planning?
   - How to handle users who upvoted but then can't attend?

5. **Event Creator Special Powers**
   - Can creator override votes and pick any date?
   - Can creator remove supply items others added?
   - Can creator remove planning participants?

### Business Logic

6. **Minimum Requirements for SCHEDULED Status**
   - Need minimum X committed attendees?
   - Need minimum % of supplies fulfilled?
   - Or just need confirmed date?

7. **Changing Plans After Scheduled**
   - Can event go back to PLANNING if date needs to change?
   - What if key people drop out after scheduled?
   - Re-voting on dates or creator manually updates?

8. **Supply Item Edge Cases**
   - What if more quantity committed than needed?
   - What if same user commits twice (shouldn't happen with unique_together)?
   - What if supply item deleted - what happens to commitments?

---

## Design Patterns to Consider

### 1. State Machine Pattern
Your Event status is a state machine. Consider documenting allowed transitions:
```
PROPOSAL → PLANNING → SCHEDULED → COMPLETED
               ↓           ↓
            ARCHIVED   ARCHIVED
```

Think about what happens if status changes incorrectly.

### 2. Manager Methods
Consider adding custom managers for common queries:
```python
class SupplyItemManager(models.Manager):
    def fulfilled(self):
        return self.filter(quantity_committed__gte=models.F('quantity_needed'))

    def unfulfilled(self):
        return self.filter(quantity_committed__lt=models.F('quantity_needed'))
```

### 3. Signals for Side Effects
Consider using signals for:
- Auto-creating Plan when Event → PLANNING
- Sending notifications on status changes
- Updating Plan.volunteers based on AttendanceCommitment

### 4. Template Partials
Break large templates into reusable partials:
- `events/partials/date_voting.html`
- `events/partials/supply_list.html`
- `events/partials/attendance_commitment.html`

Keeps event_detail.html manageable and components reusable.

---

## Success Criteria

✅ **You're done when:**
- [ ] Events automatically transition to PLANNING when upvote threshold reached
- [ ] Plan is auto-created for planning events
- [ ] Users can propose and vote on dates
- [ ] Event creator can confirm winning date → SCHEDULED status
- [ ] Users can add supply items to the list
- [ ] Users can commit to bringing supplies
- [ ] Supply quantities update correctly
- [ ] Users can set attendance commitment (Yes/Maybe/No)
- [ ] Event detail page shows appropriate interface based on status
- [ ] All planning features have permission checks
- [ ] Upvoters receive notifications when event moves to PLANNING
- [ ] Test coverage for all new models and views
- [ ] No obvious bugs in the workflow
- [ ] Mobile responsive design

---

## Next Steps After Completion

Once you've implemented this feature, you'll be ready for:
1. **Event Check-in System** (QR codes, geofencing)
2. **User Profile Enhancements** (show event participation history)
3. **Testing Expansion** (increase coverage to 80%+)
4. **Notification System** (expand beyond basic notifications)

---

## Questions to Think About Before Starting

1. Should you create Django forms for the models, or handle validation in views?
2. Will you use class-based views or function-based views?
3. How will you handle errors (form validation errors, permission errors)?
4. What should happen to planning data if event is archived?
5. Should there be time limits (e.g., planning must complete within 30 days)?
6. Do you want real-time updates (HTMX/Alpine.js) or traditional form submissions?

---

**Good luck! Take it one phase at a time, test as you go, and don't hesitate to ask questions when you're stuck or want to discuss trade-offs!**
