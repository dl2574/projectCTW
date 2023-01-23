from django.test import TestCase, SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from .models import User
from selenium import webdriver
from selenium.webdriver.common.by import By




class UserModelTests(TestCase):
    def test_user_model_exists(self):
        users = list(User.objects.all())
        self.assertEqual(users, [])

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
        self.assertContains(response, f'<form method="POST" action={reverse("login")}>')
        self.assertNotContains(response, "<h3>Register</h3>")


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
        self.assertContains(response, f'<form method="POST" action={reverse("register")}>')
        self.assertNotContains(response, "<h3>Login</h3>")


