from django.test import TestCase
from django.urls import reverse


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
        self.assertContains(response, "Sign up for an account")
        self.assertNotContains(response, "Sign in")


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
        self.assertContains(response, "Sign in to your account")
        self.assertNotContains(response, "Sign up")
