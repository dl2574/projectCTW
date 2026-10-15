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
        self.assertContains(
            self.response, f'id="event-card-{self.test_event.id}"')
        # Upvote count is 1 after voting
        self.assertContains(
            self.response, "<span class=\"text-xs font-semibold\">1</span>")

        # Voting again removes the upvote; count drops back to 0
        self.response = self.client.post(
            reverse("upvote", kwargs={'pk': self.test_event.id}))
        self.assertContains(
            self.response, "<span class=\"text-xs font-semibold\">0</span>")


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

        # Add test to confirm that the header upvote button works and updates
        # correctly.


class TestUpvoteProposalPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.UserModel = get_user_model()
        cls.creator = cls.UserModel.objects.create_user(
            username="creator",
            email="creator@mail.com",
            password="testpass123",
        )

        cls.voter = cls.UserModel.objects.create_user(
            username="voter",
            email="voter@mail.com",
            password="testpass123",
        )

        cls.test_event = Event.objects.create(
            name="test_event",
            description="event for testing",
            location="online",
            created_by=cls.creator,
        )

    def test_upvote_requires_authentication(self):
        response = self.client.post(
            reverse("upvote", kwargs={"pk": self.test_event.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_upvote_from_proposal_page(self):
        self.client.login(email=self.voter.email, password="testpass123")

        response = self.client.post(
            reverse("upvote", kwargs={"pk": self.test_event.id}),
            HTTP_HX_TARGET=f"event-card-{self.test_event.id}",
        )

        # Check for response code
        self.assertEqual(response.status_code, 200)

        # Check response template contains correct number of upvotes (1)
        self.assertContains(
            response, '<span class="text-xs font-semibold">1</span>')

        # Check response template contains correct upvote button style
        self.assertContains(response, 'text-teal-700">Upvote</span>')

    def test_upvote_removed_if_posted_a_second_time(self):
        self.client.login(email=self.voter.email, password="testpass123")

        post_url = reverse("upvote", kwargs={"pk": self.test_event.id})
        hx_target = f"event-card-{self.test_event.id}"

        # Add an upvote from the user
        _ = self.client.post(post_url, HTTP_HX_TARGET=hx_target)

        # Remove that upvote just added
        response = self.client.post(post_url, HTTP_HX_TARGET=hx_target)

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response, '<span class="text-xs font-semibold">0</span>'
        )

        self.assertContains(
            response, '<span class="">Upvote</span>'
        )

        self.assertEqual(self.test_event.upvotes.count(), 0)


class TestEditEventAuthorization(TestCase):
    """Only an event's creator may edit it. Denial tests also assert the DB row
    is unchanged: a view could reject the user yet still have saved the form."""

    password = "testpass123"

    @classmethod
    def setUpTestData(cls):
        cls.UserModel = get_user_model()
        cls.creator = cls.UserModel.objects.create_user(
            username="edit_creator",
            email="edit_creator@email.com",
            password=cls.password,
        )
        cls.other_user = cls.UserModel.objects.create_user(
            username="edit_other",
            email="edit_other@email.com",
            password=cls.password,
        )
        cls.test_event = Event.objects.create(
            name="original name",
            description="original description",
            location="original location",
            created_by=cls.creator,
        )
        cls.url = reverse("editEvent", kwargs={"pk": cls.test_event.pk})
        cls.edit_data = {
            "name": "tampered name",
            "description": "tampered description",
            "location": "tampered location",
        }

    def assertEventUnchanged(self):
        self.test_event.refresh_from_db()
        self.assertEqual(self.test_event.name, "original name")
        self.assertEqual(self.test_event.description, "original description")
        self.assertEqual(self.test_event.location, "original location")

    def test_anonymous_get_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next={self.url}"
        )

    def test_anonymous_post_redirects_to_login_and_does_not_edit(self):
        response = self.client.post(self.url, self.edit_data)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next={self.url}"
        )
        self.assertEventUnchanged()

    def test_non_creator_get_is_forbidden(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateNotUsed(response, "events/event_form.html")

    def test_non_creator_post_is_forbidden_and_does_not_edit(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.url, self.edit_data)
        self.assertEqual(response.status_code, 403)
        self.assertEventUnchanged()

    def test_creator_get_renders_prefilled_form(self):
        self.client.force_login(self.creator)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_form.html")
        self.assertEqual(response.context["form"].instance, self.test_event)

    def test_creator_post_edits_event(self):
        # Positive control: proves the denial tests pass because of the
        # creator check, not because editing is broken for everyone.
        self.client.force_login(self.creator)
        response = self.client.post(self.url, self.edit_data)
        self.assertRedirects(response, self.test_event.get_absolute_url())
        self.test_event.refresh_from_db()
        self.assertEqual(self.test_event.name, "tampered name")

    def test_nonexistent_event_returns_404(self):
        self.client.force_login(self.creator)
        url = reverse(
            "editEvent", kwargs={"pk": "00000000-0000-0000-0000-000000000000"}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
