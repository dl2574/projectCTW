from django.test import SimpleTestCase
from django.urls import reverse


class RegisterpageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/account/register/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("register"))
        self.assertTemplateUsed(response, "userProfile/login_register.html")

    def test_template_content(self):
        response = self.client.get(reverse("register"))
        self.assertContains(
            response, f'<form method="POST" action={reverse("register")}>')
        self.assertNotContains(response, "<h3>Login</h3>")


class LoginpageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/account/login/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("login"))
        self.assertTemplateUsed(response, "userProfile/login_register.html")

    def test_template_content(self):
        response = self.client.get(reverse("login"))
        self.assertContains(
            response, f'<form method="POST" action={reverse("login")}>')
        self.assertNotContains(response, "<h3>Register</h3>")
