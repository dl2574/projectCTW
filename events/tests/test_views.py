from django.test import TestCase
from django.contrib.auth import get_user_model, get_user
from django.urls import reverse

from ..models import Event

class TestProposals(TestCase):
    password = "testpass123"
    
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("proposals")
        
        cls.UserModel = get_user_model()
        cls.test_user1 = cls.UserModel.objects.create_user(
            username = "testuser1",
            email = "testuser1@email.com",
            password = cls.password
        )
        
        cls.test_user2 = cls.UserModel.objects.create_user(
            username = "testuser2",
            email = "testuser2@email.com",
            password = cls.password
        )
        
        cls.test_event = Event.objects.create(
            name = "testevent",
            description = "test event description",
            location = "the web",
            created_by = cls.test_user1,
        )
        
        
    def test_proposal_template(self):
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "events/proposed_events.html")
        self.assertContains(self.response, "Proposed Events")
        
        
    def test_proposal_event_exisits(self):
        self.response = self.client.get(self.url)
        self.assertContains(self.response, self.test_event.description)
    
    def test_proposal_upvote(self):
        self.client.login(
            email = self.test_user2.email, 
            password = self.password,
        )
        self.assertTrue(get_user(self.client).is_authenticated)
        
        # Create 1 upvote
        self.response = self.client.post(reverse("upvote", kwargs={'pk':self.test_event.id}))
        self.assertContains(self.response, "1 Up Vote")
        
        # Remove 1 upvote when user has already upvoted
        self.response = self.client.post(reverse("upvote", kwargs={'pk':self.test_event.id}))
        self.assertContains(self.response, "0 Up Votes")
        
        
        