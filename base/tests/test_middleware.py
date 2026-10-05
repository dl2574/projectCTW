from django.test import RequestFactory, SimpleTestCase
from django.http import HttpResponseRedirect, HttpResponse

from ..middleware import HxRedirectMiddleware


class BaseMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_htmx_and_redirect(self):
        redirect_path="/login/"
        
        def temp_get_response(request):
            test_response = HttpResponseRedirect(redirect_path)
            return test_response

        request = self.factory.get(
            "/",
            headers={"HX-Request": "true",},
        )

        middleware = HxRedirectMiddleware(temp_get_response)

        response = middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Redirect"], redirect_path)

    def test_non_htmx_redirect_untouched(self):
        redirect_path="/login/"

        def temp_get_response(request):
            test_response = HttpResponseRedirect(redirect_path)
            return test_response

        request = self.factory.get(
            "/",
        )

        middleware = HxRedirectMiddleware(temp_get_response)

        response = middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("HX-Redirect", response)

    def test_htmx_request_with_no_redirect(self):
        def temp_get_response(request):
            test_response = HttpResponse("OK")
            return test_response

        request = self.factory.get(
            "/",
            headers={"HX-Request": "true",},
        )

        middleware = HxRedirectMiddleware(temp_get_response)

        response = middleware(request)

        self.assertNotIn("HX-Redirect", response)
