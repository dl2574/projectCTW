from django.test import TestCase, SimpleTestCase, SimpleUploadedFile
from ..forms import CustomUserCreationForm, CustomUserChangeForm
from ..models import User

from io import BytesIO
from PIL import Image


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


class UserChangeFormTests(SimpleTestCase):
    def make_image_file(self, size=None):
        pass

    def test_profile_picture_oversized(self):
        pass

    def test_profile_picture_correct_size(self):
        pass

    def test_profile_picture_not_image(self):
        pass
