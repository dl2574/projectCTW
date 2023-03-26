from django.test import TestCase
from ..forms import CustomUserCreationForm
from ..models import User


class UserFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            "johnblack", "john@black.com", "12345")

    def test_unique_email_field(self):
        data = {
            "first_name": "john",
            "last_name": "black",
            "email": "john@black.com",
            "password1": "12345",
            "password2": "12345"
        }
        form = CustomUserCreationForm(data)
        self.assertFormError(form=form, field="email",
                             errors="User with this Email already exists.")

    def test_unique_username_field(self):
        data = {
            "first_name": "john",
            "last_name": "black",
            "username": "johnblack",
            "password1": "12345",
            "password2": "12345"
        }
        form = CustomUserCreationForm(data)
        self.assertFormError(form=form, field="username",
                             errors="A user with that username already exists.")
