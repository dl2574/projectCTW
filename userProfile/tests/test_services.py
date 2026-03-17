from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from events.models import AttendanceCommitment, Event, Plan
from userProfile.services import email_event_status_update

from unittest.mock import patch
from anymail.exceptions import AnymailError

User = get_user_model()


# override_settings swaps in Django's in-memory email backend so no real
# emails are sent during tests. Sent messages accumulate in mail.outbox.
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EmailEventStatusUpdateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.upvoter = User.objects.create_user(
            username="upvoter", email="upvoter@email.com", password="testpass123"
        )
        cls.attendee = User.objects.create_user(
            username="attendee", email="attendee@email.com", password="testpass123"
        )
        cls.opted_out = User.objects.create_user(
            username="optedout",
            email="optedout@email.com",
            password="testpass123",
            email_status_updates=False,
        )
        cls.event = Event.objects.create(
            name="Park Cleanup",
            description="desc",
            location="Central Park",
            created_by=cls.upvoter,
        )
        cls.event.upvotes.add(cls.upvoter)
        cls.plan = Plan.objects.create(event=cls.event)
        AttendanceCommitment.objects.create(
            plan=cls.plan,
            user=cls.attendee,
            status=AttendanceCommitment.CommitmentStatus.YES,
        )
        # opted_out also upvoted — should NOT receive an email
        cls.event.upvotes.add(cls.opted_out)

    def test_sends_to_upvoter(self):
        email_event_status_update(self.event)
        recipients = [msg.to[0] for msg in mail.outbox]
        self.assertIn(self.upvoter.email, recipients)

    def test_sends_to_committed_attendee(self):
        email_event_status_update(self.event)
        recipients = [msg.to[0] for msg in mail.outbox]
        self.assertIn(self.attendee.email, recipients)

    def test_does_not_send_to_opted_out_user(self):
        email_event_status_update(self.event)
        recipients = [msg.to[0] for msg in mail.outbox]
        self.assertNotIn(self.opted_out.email, recipients)

    def test_no_duplicate_email_when_user_upvoted_and_committed(self):
        # A user who both upvoted and has an attendance commitment should only
        # receive one email, not two.
        AttendanceCommitment.objects.create(
            plan=self.plan,
            user=self.upvoter,
            status=AttendanceCommitment.CommitmentStatus.YES,
        )
        email_event_status_update(self.event)
        upvoter_emails = [
            msg for msg in mail.outbox if msg.to[0] == self.upvoter.email]
        self.assertEqual(len(upvoter_emails), 1)

    def test_subject_contains_event_name(self):
        email_event_status_update(self.event)
        self.assertIn(self.event.name, mail.outbox[0].subject)

    def test_no_emails_sent_when_all_opted_out(self):
        # Sanity check: if nobody wants emails, outbox should stay empty.
        event = Event.objects.create(
            name="Quiet Event",
            description="desc",
            location="loc",
            created_by=self.opted_out,
        )
        event.upvotes.add(self.opted_out)
        email_event_status_update(event)
        self.assertEqual(len(mail.outbox), 0)


class TestEmailErors(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            email='test_user@mail.com',
            email_status_updates=True,
        )

        cls.test_event = Event.objects.create(
            name='test_event',
            description='event for testing',
            location='online',
            created_by=cls.test_user,
        )

        cls.test_event.upvotes.add(cls.test_user)

    @patch('userProfile.services.send_mail')
    def test_anymail_exception_is_captured_and_logged(self, mock_send_mail):
        mock_send_mail.side_effect = AnymailError("API error")

        with self.assertLogs('userProfile.services', level='ERROR') as log:
            email_event_status_update(self.test_event)
            self.assertIn("Email Error", log.output[0])

    @patch('userProfile.services.send_mail')
    def test_connectionerror_exception_is_captured_and_logged(self, mock_send_mail):
        mock_send_mail.side_effect = ConnectionError("Connection error")

        with self.assertLogs('userProfile.services', level='ERROR') as log:
            email_event_status_update(self.test_event)
            self.assertIn("Email Error", log.output[0])
