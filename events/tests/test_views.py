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
            username="testuser1",
            email="testuser1@email.com",
            password=cls.password
        )

        cls.test_user2 = cls.UserModel.objects.create_user(
            username="testuser2",
            email="testuser2@email.com",
            password=cls.password
        )

        cls.test_event = Event.objects.create(
            name="testevent",
            description="test event description",
            location="the web",
            created_by=cls.test_user1,
        )

    def test_proposal_template(self):
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "events/proposed_events.html")
        self.assertContains(self.response, "Event Proposals")

    def test_proposal_event_exisits(self):
        self.response = self.client.get(self.url)
        self.assertContains(self.response, self.test_event.description)

    def test_proposal_upvote(self):
        self.client.login(
            email=self.test_user2.email,
            password=self.password,
        )
        self.assertTrue(get_user(self.client).is_authenticated)

        # Upvoting returns the updated event card partial — check for the
        # event name and the upvote count embedded in the card HTML.
        self.response = self.client.post(
            reverse("upvote", kwargs={'pk': self.test_event.id}))
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, self.test_event.name)
        self.assertContains(self.response, f'id="event-card-{self.test_event.id}"')
        # Upvote count is 1 after voting
        self.assertContains(self.response, "<span class=\"text-xs font-semibold\">1</span>")

        # Voting again removes the upvote; count drops back to 0
        self.response = self.client.post(
            reverse("upvote", kwargs={'pk': self.test_event.id}))
        self.assertContains(self.response, "<span class=\"text-xs font-semibold\">0</span>")


class TestUpvoteDetailPage(TestCase):
    """Upvoting from the event detail page returns both the primary event-header
    partial and an out-of-band sidebar-upvote-count fragment so both DOM regions
    update in a single round-trip."""

    password = "testpass123"

    @classmethod
    def setUpTestData(cls):
        cls.UserModel = get_user_model()
        cls.creator = cls.UserModel.objects.create_user(
            username="detail_creator",
            email="detail_creator@email.com",
            password=cls.password,
        )
        cls.voter = cls.UserModel.objects.create_user(
            username="detail_voter",
            email="detail_voter@email.com",
            password=cls.password,
        )
        cls.test_event = Event.objects.create(
            name="detail_test_event",
            description="an event for detail-page upvote tests",
            location="the web",
            created_by=cls.creator,
        )

    def test_upvote_from_detail_page_returns_oob_sidebar_fragment(self):
        self.client.login(email=self.voter.email, password=self.password)

        response = self.client.post(
            reverse("upvote", kwargs={"pk": self.test_event.id}),
            HTTP_HX_TARGET="event-header",
        )

        self.assertEqual(response.status_code, 200)

        # Primary swap: the event-header section must be present
        self.assertContains(response, 'id="event-header"')

        # OOB swap: the sidebar fragment must be present with the OOB attribute
        self.assertContains(response, 'id="sidebar-upvote-count"')
        self.assertContains(response, 'hx-swap-oob="outerHTML"')

        # Both locations should reflect the updated count of 1
        self.assertContains(response, '<span class="font-semibold">1</span>')

    def test_upvote_toggle_from_detail_page_decrements_sidebar(self):
        self.client.login(email=self.voter.email, password=self.password)
        upvote_url = reverse("upvote", kwargs={"pk": self.test_event.id})

        # First click: add upvote
        self.client.post(upvote_url, HTTP_HX_TARGET="event-header")

        # Second click: remove upvote — count should drop back to 0
        response = self.client.post(upvote_url, HTTP_HX_TARGET="event-header")
        self.assertContains(response, '<span class="font-semibold">0</span>')
