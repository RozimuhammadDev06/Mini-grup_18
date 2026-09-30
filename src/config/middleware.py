import json

from django.http import JsonResponse


class APIExceptionJSONMiddleware:
    """
    /api/ manzillarida kutilmagan xatolarni JSON formatida qaytaradi.
    """

    def __init__(self, get_response ):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)

        except Exception as exc:
            if request.path.startswith("/api/"):
                return JsonResponse(
                    {
                        "success": False,
                        "status_code": 500,
                        "error": "Internal server error.",
                    },
                    status=500,
                )

            raise exc
