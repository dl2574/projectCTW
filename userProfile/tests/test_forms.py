from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
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


class UserChangeFormTests(TestCase):
    def make_image_file(self, size=None):
        image_content = Image.new('RGB', (100, 100))
        buffer = BytesIO()
        image_content.save(buffer, format="JPEG")

        if size == "large":
            return SimpleUploadedFile("test_photo.jpg", buffer.getvalue() + (b"\00" * (1024 * 1024 * 2 + 1)), content_type="image/jpeg")
        else:
            return SimpleUploadedFile("test_photo.jpg", buffer.getvalue(), content_type="image/jpeg")

    def test_profile_picture_oversized(self):
        image = self.make_image_file("large")
        form = CustomUserChangeForm({}, {"profile_picture": image})
        self.assertFormError(form=form, field="profile_picture",
                             errors=f"File size must be under {
                                 CustomUserChangeForm.MAX_PROFILE_PICTURE_SIZE / (1024 * 1024):.2f} MB.")

    def test_profile_picture_correct_size(self):
        image = self.make_image_file()
        form = CustomUserChangeForm({
            "email": "testuser@mail.com",
            "username": "testuser",
            "first_name": "test",
            "last_name": "user",
        }, {"profile_picture": image})
        self.assertTrue(form.is_valid())

    def test_profile_picture_not_image(self):
        image = SimpleUploadedFile(
            "bad_photo.jpg", b"randomness", content_type="image/jpeg")
        form = CustomUserChangeForm({}, {"profile_picture": image})
        self.assertFormError(form=form, field="profile_picture",
                             errors="Upload a valid image. The file you uploaded was either not an image or a corrupted image.")
