from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import News, Promotion


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


class NewsPublishPermissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="news-publisher",
            email="jasur1@gmail.com",
            password="test-password",
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.payload = {
            "title": "Marketing announcement",
            "content": "Announcement content",
        }

    def test_user_with_add_news_permission_can_create_news(self):
        content_type = ContentType.objects.get_for_model(News)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="add_news",
        )
        self.user.user_permissions.add(permission)

        response = self.client.post(
            "/api/news/",
            self.payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            News.objects.filter(title="Marketing announcement").exists()
        )

    def test_user_with_add_news_permission_cannot_edit_news(self):
        content_type = ContentType.objects.get_for_model(News)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="add_news",
        )
        self.user.user_permissions.add(permission)
        news = News.objects.create(title="Existing announcement")

        response = self.client.patch(
            f"/api/news/{news.pk}/",
            {"title": "Changed announcement"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        news.refresh_from_db()
        self.assertEqual(news.title, "Existing announcement")
