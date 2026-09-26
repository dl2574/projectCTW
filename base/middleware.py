class HxRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.headers.get('HX-Request') and 300 <= response.status_code < 400:
            response['HX-Redirect'] = response['Location']
            # Update status code so the browser doesn't auto redirect and allows
            # htmx the chance to handle the request.
            response.status_code = 200
        return response
