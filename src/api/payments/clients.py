import requests

from django.conf import settings


class FintechhubClient:
    def __init__(self ):
        self.base_url = settings.FHP_BASE_URL.rstrip("/")
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
    ):
        url = f"{self.base_url}{path}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        return requests.request(
            method=method,
            url=url,
            json=json_data,
            headers=headers,
            timeout=self.timeout,
        )
