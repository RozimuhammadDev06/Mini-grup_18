from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class LoginAddressAuthenticationTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="address-user",
            email="address-user@example.com",
            password="StrongPassword123!",
        )

    def test_login_returns_standard_and_legacy_token_fields(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.user.email,
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["access"], response.data["access_token"])
        self.assertEqual(response.data["refresh"], response.data["refresh_token"])

    def test_login_access_token_authorizes_address_list(self):
        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.user.email,
                "password": "StrongPassword123!",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        address_response = self.client.get(
            reverse("user-address-list"),
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}",
        )

        self.assertEqual(address_response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_create_address(self):
        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.user.email,
                "password": "StrongPassword123!",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("user-address-list"),
            {
                "company_name": "cerv",
                "street": "egvetg",
                "house": "64",
                "phone": "+9985205252",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "cerv")

    def test_address_list_still_requires_authentication(self):
        response = self.client.get(reverse("user-address-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
