import requests

from django.conf import settings


class FintechhubClient:
    def __init__(self, base_url=None):
        self.base_url = (base_url or settings.FHP_BASE_URL).rstrip("/")
        self.timeout = getattr(
            settings,
            "FHP_TIMEOUT",
            20,
        )

    def request(
        self,
        method,
        path,
        json_data=None,
        authorization=None,
    ):
        url = f"{self.base_url}{path}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if authorization:
            headers["Authorization"] = authorization

        return requests.request(
            method=method,
            url=url,
            json=json_data,
            headers=headers,
            timeout=self.timeout,
        )
