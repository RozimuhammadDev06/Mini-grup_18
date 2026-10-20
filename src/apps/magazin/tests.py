from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Promotion


class PromotionListTests(TestCase):
    def test_list_returns_promotions(self):
        now = timezone.now()
        Promotion.objects.create(
            title="Test promotion",
            description="",
            discount_value="10.00",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
            is_active=True,
        )

        response = APIClient().get("/api/promotions/?page_size=1000")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Test promotion")
