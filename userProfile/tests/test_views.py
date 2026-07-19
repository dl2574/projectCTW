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
