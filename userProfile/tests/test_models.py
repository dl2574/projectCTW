from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
            first_name="Jane",
            last_name="Doe",
        )

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Jane Doe")

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), "Jane D")

    def test_email_status_updates_defaults_to_true(self):
        # Opt-out model: new users receive status emails unless they turn it off.
        self.assertTrue(self.user.email_status_updates)

    def test_email_event_reminders_defaults_to_true(self):
        # Same opt-out policy for reminder emails.
        self.assertTrue(self.user.email_event_reminders)

    def test_can_opt_out_of_status_updates(self):
        self.user.email_status_updates = False
        self.user.save(update_fields=["email_status_updates"])
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_status_updates)

    def test_can_opt_out_of_event_reminders(self):
        self.user.email_event_reminders = False
        self.user.save(update_fields=["email_event_reminders"])
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_event_reminders)
