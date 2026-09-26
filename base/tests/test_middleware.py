from django.test import RequestFactory, SimpleTestCase

from ..middleware import HxRedirectMiddleware


class BaseMiddlewareTests(SimpleTestCase):
    @classmethod
    def setUpTestData(cls):
        pass
