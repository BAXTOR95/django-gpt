import logging

logger = logging.getLogger(__name__)


class RateLimitLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 429:
            logger.warning(f"Rate limit exceeded for IP: {request.META['REMOTE_ADDR']}")

        return response
