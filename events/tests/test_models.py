from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from ..models import (
    AttendanceCommitment,
    Event,
    Plan,
    SupplyCommitment,
    SupplyItem,
)

User = get_user_model()


class EventModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
        )
        cls.event = Event.objects.create(
            name="testEvent",
            description="testdescription",
            location="location",
            created_by=cls.user,
        )
        cls.event.upvotes.add(cls.user)

    def test_event_creation(self):
        self.assertEqual(self.event.name, "testEvent")
        self.assertEqual(self.event.description, "testdescription")
        self.assertEqual(self.event.location, "location")
        self.assertEqual(self.event.created_by, self.user)
        self.assertEqual(self.event.upvotes.get(pk=self.user.pk), self.user)
        self.assertEqual(self.event.upvotes.count(), 1)

    def test_selected_date_fields_are_nullable(self):
        # All three date confirmation fields were added last session and must
        # default to null so existing events aren't broken on migration.
        self.assertIsNone(self.event.selected_date)
        self.assertIsNone(self.event.date_confirmed_by)
        self.assertIsNone(self.event.date_confirmed_on)

    def test_number_of_upvotes(self):
        self.assertEqual(self.event.number_of_upvotes(), 1)

    def test_user_upvoted_returns_true_for_upvoter(self):
        self.assertTrue(self.event.user_upvoted(self.user))

    def test_user_upvoted_returns_false_for_non_upvoter(self):
        other = User.objects.create_user(
            username="other", email="other@email.com", password="testpass123"
        )
        self.assertFalse(self.event.user_upvoted(other))

    def test_set_required_num_upvotes_positive(self):
        # Method should update the attribute and signal success with True.
        result = self.event.set_required_num_upvotes(10)
        self.assertTrue(result)
        self.assertEqual(self.event.required_num_upvotes, 10)

    def test_set_required_num_upvotes_zero_returns_false(self):
        # Zero volunteers makes no sense as a threshold; method should reject
        # it and leave the existing value unchanged.
        self.event.refresh_from_db()  # reset any in-memory mutation from other tests
        original = self.event.required_num_upvotes
        result = self.event.set_required_num_upvotes(0)
        self.assertFalse(result)
        self.assertEqual(self.event.required_num_upvotes, original)


class PlanModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_yes = User.objects.create_user(
            username="user_yes", email="yes@email.com", password="testpass123"
        )
        cls.user_maybe = User.objects.create_user(
            username="user_maybe", email="maybe@email.com", password="testpass123"
        )
        cls.user_no = User.objects.create_user(
            username="user_no", email="no@email.com", password="testpass123"
        )
        cls.event = Event.objects.create(
            name="Plan Event",
            description="desc",
            location="loc",
            created_by=cls.user_yes,
        )
        cls.plan = Plan.objects.create(event=cls.event)
        AttendanceCommitment.objects.create(
            plan=cls.plan,
            user=cls.user_yes,
            status=AttendanceCommitment.CommitmentStatus.YES,
        )
        AttendanceCommitment.objects.create(
            plan=cls.plan,
            user=cls.user_maybe,
            status=AttendanceCommitment.CommitmentStatus.MAYBE,
        )
        AttendanceCommitment.objects.create(
            plan=cls.plan,
            user=cls.user_no,
            status=AttendanceCommitment.CommitmentStatus.NO,
        )

    def test_confirmed_attendees_returns_yes_users(self):
        confirmed = self.plan.confirmed_attendees()
        self.assertIn(self.user_yes, confirmed)

    def test_confirmed_attendees_excludes_maybe_and_no(self):
        confirmed = self.plan.confirmed_attendees()
        self.assertNotIn(self.user_maybe, confirmed)
        self.assertNotIn(self.user_no, confirmed)

    def test_maybe_attendees_returns_maybe_users(self):
        maybe = self.plan.maybe_attendees()
        self.assertIn(self.user_maybe, maybe)
        self.assertNotIn(self.user_yes, maybe)
        self.assertNotIn(self.user_no, maybe)

    def test_attendance_counts_returns_correct_dict(self):
        counts = self.plan.attendance_counts()
        self.assertEqual(counts['yes'], 1)
        self.assertEqual(counts['maybe'], 1)
        self.assertEqual(counts['no'], 1)


class AttendanceCommitmentModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="attendee", email="attendee@email.com", password="testpass123"
        )
        cls.event = Event.objects.create(
            name="Attendance Event",
            description="desc",
            location="loc",
            created_by=cls.user,
        )
        cls.plan = Plan.objects.create(event=cls.event)

    def test_create_with_yes_status(self):
        commitment = AttendanceCommitment.objects.create(
            plan=self.plan,
            user=self.user,
            status=AttendanceCommitment.CommitmentStatus.YES,
        )
        self.assertEqual(commitment.status, "YES")
        self.assertEqual(commitment.plan, self.plan)
        self.assertEqual(commitment.user, self.user)

    def test_create_with_maybe_status(self):
        commitment = AttendanceCommitment.objects.create(
            plan=self.plan,
            user=self.user,
            status=AttendanceCommitment.CommitmentStatus.MAYBE,
        )
        self.assertEqual(commitment.status, "MAYBE")

    def test_create_with_no_status(self):
        commitment = AttendanceCommitment.objects.create(
            plan=self.plan,
            user=self.user,
            status=AttendanceCommitment.CommitmentStatus.NO,
        )
        self.assertEqual(commitment.status, "NO")

    def test_unique_together_prevents_duplicate_commitment(self):
        # A user should only be able to express one attendance intent per plan.
        # Changing it should go through update, not a second create.
        AttendanceCommitment.objects.create(
            plan=self.plan,
            user=self.user,
            status=AttendanceCommitment.CommitmentStatus.YES,
        )
        with self.assertRaises(IntegrityError):
            AttendanceCommitment.objects.create(
                plan=self.plan,
                user=self.user,
                status=AttendanceCommitment.CommitmentStatus.NO,
            )


class SupplyItemModelTests(TestCase):
    # Tests for is_fulfilled() and remaining_needed() use unsaved model instances
    # because both methods only read self.quantity_needed and self.quantity_committed
    # — no DB query needed. This keeps these tests fast and focused on pure logic.

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="supplier", email="supplier@email.com", password="testpass123"
        )
        cls.event = Event.objects.create(
            name="Supply Event",
            description="desc",
            location="loc",
            created_by=cls.user,
        )
        cls.plan = Plan.objects.create(event=cls.event)

    def test_is_fulfilled_returns_false_when_under_quantity(self):
        item = SupplyItem(quantity_needed=5, quantity_committed=3)
        self.assertFalse(item.is_fulfilled())

    def test_is_fulfilled_returns_true_when_at_quantity(self):
        item = SupplyItem(quantity_needed=5, quantity_committed=5)
        self.assertTrue(item.is_fulfilled())

    def test_is_fulfilled_returns_true_when_over_quantity(self):
        # Over-committing still counts as fulfilled
        item = SupplyItem(quantity_needed=5, quantity_committed=10)
        self.assertTrue(item.is_fulfilled())

    def test_remaining_needed_calculates_correctly(self):
        item = SupplyItem(quantity_needed=5, quantity_committed=3)
        self.assertEqual(item.remaining_needed(), 2)

    def test_remaining_needed_returns_zero_when_overfulfilled(self):
        # max(0, ...) in remaining_needed() prevents a negative return value
        item = SupplyItem(quantity_needed=5, quantity_committed=10)
        self.assertEqual(item.remaining_needed(), 0)

    def test_update_committed_quantity_aggregates_all_commitments(self):
        # update_committed_quantity() should sum all child SupplyCommitment
        # quantities and write the result back to the parent item.
        item = SupplyItem.objects.create(
            plan=self.plan,
            name="Shovels",
            quantity_needed=10,
            created_by=self.user,
        )
        user2 = User.objects.create_user(
            username="supplier2", email="supplier2@email.com", password="testpass123"
        )
        # SupplyCommitment.save() calls update_committed_quantity() automatically,
        # so we just verify the final DB value after two commitments.
        SupplyCommitment.objects.create(supply_item=item, user=self.user, quantity=3)
        SupplyCommitment.objects.create(supply_item=item, user=user2, quantity=4)

        item.refresh_from_db()
        self.assertEqual(item.quantity_committed, 7)


class SupplyCommitmentModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="committer", email="committer@email.com", password="testpass123"
        )
        cls.user2 = User.objects.create_user(
            username="committer2", email="committer2@email.com", password="testpass123"
        )
        cls.event = Event.objects.create(
            name="Commitment Event",
            description="desc",
            location="loc",
            created_by=cls.user,
        )
        cls.plan = Plan.objects.create(event=cls.event)
        cls.supply_item = SupplyItem.objects.create(
            plan=cls.plan,
            name="Gloves",
            quantity_needed=10,
            created_by=cls.user,
        )

    def test_save_updates_parent_supply_item_quantity(self):
        # Overridden save() must keep the parent item's quantity_committed in sync.
        SupplyCommitment.objects.create(
            supply_item=self.supply_item, user=self.user, quantity=5
        )
        self.supply_item.refresh_from_db()
        self.assertEqual(self.supply_item.quantity_committed, 5)

    def test_multiple_commitments_are_summed_correctly(self):
        SupplyCommitment.objects.create(
            supply_item=self.supply_item, user=self.user, quantity=3
        )
        SupplyCommitment.objects.create(
            supply_item=self.supply_item, user=self.user2, quantity=4
        )
        self.supply_item.refresh_from_db()
        self.assertEqual(self.supply_item.quantity_committed, 7)

    def test_delete_decrements_parent_supply_item_quantity(self):
        # Overridden delete() must also keep the parent in sync, so the item
        # doesn't appear fulfilled after a commitment is withdrawn.
        commitment = SupplyCommitment.objects.create(
            supply_item=self.supply_item, user=self.user, quantity=5
        )
        commitment.delete()
        self.supply_item.refresh_from_db()
        self.assertEqual(self.supply_item.quantity_committed, 0)

    def test_unique_together_prevents_duplicate_commitment(self):
        # Each user can only commit once per supply item.
        # To adjust quantity they must update their existing commitment.
        SupplyCommitment.objects.create(
            supply_item=self.supply_item, user=self.user, quantity=2
        )
        with self.assertRaises(IntegrityError):
            SupplyCommitment.objects.create(
                supply_item=self.supply_item, user=self.user, quantity=3
            )
