from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress


class RegisterpageTests(TestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("account_signup"))
        self.assertTemplateUsed(response, "account/signup.html")

    def test_template_content(self):
        response = self.client.get(reverse("account_signup"))
        self.assertContains(response, "Join the movement")
        self.assertContains(response, "Create Account")


class LoginpageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "testpass123"
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="TestUser@email.com",
            password=cls.password,
            first_name="Lord",
            last_name="Fly",
        )
        cls.primary_email = EmailAddress.objects.create(
            user=cls.user,
            email=cls.user.email.lower(),
            primary=True,
            verified=True,
        )

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("account_login"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("account_login"))
        self.assertTemplateUsed(response, "account/login.html")

    def test_template_content(self):
        response = self.client.get(reverse("account_login"))
        self.assertContains(response, "Welcome back")
        self.assertContains(response, "Sign in")

    def test_login_with_mismatched_case_email(self):
        response = self.client.post(
            reverse("account_login"),
            {
                "login": "tESTuSER@email.com",
                "password": self.password,
            },
            follow=False,
        )
        self.assertEqual(response.status_code, 302)


class EmailTemplateLogicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="testpass123",
            first_name="Jane",
            last_name="Doe",
        )
        cls.primary_email = EmailAddress.objects.create(
            user=cls.user,
            email=cls.user.email,
            primary=True,
            verified=True,
        )

    def setUp(self):
        self.email = EmailAddress.objects.create(
            user=self.user,
            email="test@test.com",
            primary=False,
            verified=False,
        )

    def test_email_verified_not_primary(self):
        self.email.verified = True
        self.email.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_email"))
        self.assertContains(response, "action_primary")
        self.assertContains(response, "action_remove")
        self.assertNotContains(response, "action_send")

    def test_email_primary_and_verified(self):
        self.email.delete()
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_email"))
        self.assertNotContains(response, "action_primary")
        self.assertNotContains(response, "action_remove")
        self.assertNotContains(response, "action_send")

    def test_email_unverified_not_primary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account_email"))
        self.assertContains(response, "action_send")
        self.assertContains(response, "action_remove")
        self.assertNotContains(response, "action_primary")


class AccountProfileAuthorizationTests(TestCase):
    """Users may only view and edit their own account settings. Denial tests
    also assert the victim's row is unchanged."""

    password = "testpass123"

    @classmethod
    def setUpTestData(cls):
        cls.UserModel = get_user_model()
        cls.owner = cls.UserModel.objects.create_user(
            username="settings_owner",
            email="settings_owner@email.com",
            password=cls.password,
            bio="original bio",
        )
        cls.other_user = cls.UserModel.objects.create_user(
            username="settings_other",
            email="settings_other@email.com",
            password=cls.password,
        )
        cls.url = reverse("account_profile", kwargs={"slug": cls.owner.username})
        cls.edit_data = {
            "username": "hijacked",
            "first_name": "",
            "last_name": "",
            "bio": "tampered bio",
            "email_status_updates": "on",
            "email_event_reminders": "on",
        }

    def assertOwnerUnchanged(self):
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.username, "settings_owner")
        self.assertEqual(self.owner.bio, "original bio")

    def test_anonymous_get_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next={self.url}"
        )

    def test_other_user_get_is_forbidden(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_other_user_post_is_forbidden_and_does_not_edit(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url, self.edit_data)
        self.assertEqual(response.status_code, 403)
        self.assertOwnerUnchanged()

    def test_nonexistent_username_returns_404(self):
        # Documents current behavior: this distinguishes "doesn't exist" (404)
        # from "not yours" (403). Accepted because usernames are already public
        # via the unauthenticated profile page and event/comment bylines.
        self.client.force_login(self.other_user)
        url = reverse("account_profile", kwargs={"slug": "no-such-user"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_owner_get_renders_settings(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "userProfile/user_account.html")

    def test_owner_post_edits_account(self):
        # Positive control: proves the denial tests pass because of test_func,
        # not because the form rejects the data for everyone.
        self.client.force_login(self.owner)
        response = self.client.post(self.url, self.edit_data)
        self.assertRedirects(
            response,
            reverse("account_profile", kwargs={"slug": "hijacked"}),
        )
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.bio, "tampered bio")
