from django.test import TestCase
from ..models import User

class UserModelTests(TestCase):
    def test_user_model_exists(self):
        users = list(User.objects.all())
        self.assertEqual(users, [])
        