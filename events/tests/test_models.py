from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Event

class EventTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username = "testuser",
            email = "testuser@email.com",
            password = "testpass123" 
        )
        
        
        cls.event = Event.objects.create(
            name = "testEvent",
            description = "testdescription",
            location = "location",
            created_by = cls.user,
        )
        
        cls.event.upvotes.add(cls.user)
        
    def test_event_creation(self):
        self.assertEqual(self.event.name, "testEvent")
        self.assertEqual(self.event.description, "testdescription")
        self.assertEqual(self.event.location, "location")
        self.assertEqual(self.event.created_by, self.user)
        self.assertEqual(self.event.upvotes.get(pk=self.user.pk), self.user)
        self.assertEqual(self.event.upvotes.count(), 1)