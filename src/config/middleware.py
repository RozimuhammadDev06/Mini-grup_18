import json

from django.conf import settings
from django.http import JsonResponse


class APIExceptionJSONMiddleware:
    """
    /api/ manzillarida kutilmagan xatolarni JSON formatida qaytaradi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)

        except Exception as exc:
            if request.path.startswith("/api/"):
                error_detail = "Internal server error."
                if settings.DEBUG:
                    error_detail = f"{type(exc).__name__}: {exc}"
                return JsonResponse(
                    {
                        "success": False,
                        "status_code": 500,
                        "error": error_detail,
                    },
                    status=500,
                )

            raise exc
