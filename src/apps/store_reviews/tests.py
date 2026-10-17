"""
python manage.py test apps.store_reviews.tests
"""

import io
import shutil
import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework.test import APITestCase

from . import limits
from .models import StoreReview, StoreReviewImage

TEMP_MEDIA = tempfile.mkdtemp()
URL = "/api/v1/store-reviews/"


def make_image(name="photo.jpg", image_format="JPEG", size=(40, 30)):
    buffer = io.BytesIO()
    Image.new("RGB", size, "blue").save(buffer, format=image_format)
    content_type = f"image/{image_format.lower()}"
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)


VALID = {
    "name": "Иван Петров",
    "email": "ivan@example.test",
    "text": "Отличный магазин, большой выбор и быстрая доставка.",
}


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class StoreReviewApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()  # throttle hisoblagichini tozalash

    def post(self, data, **extra):
        return self.client.post(URL, data, format="multipart", **extra)

    # ---------- GET ----------

    def test_list_shows_only_approved_without_private_fields(self):
        StoreReview.objects.create(name="A", email="a@x.test", text="Опубликован отзыв", is_approved=True)
        StoreReview.objects.create(name="B", email="b@x.test", text="На модерации отзыв")

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        item = response.data["results"][0]
        self.assertEqual(item["name"], "A")
        self.assertNotIn("email", item)
        self.assertNotIn("ip_address", item)

    def test_list_ordering_and_pagination(self):
        for index in range(10):
            StoreReview.objects.create(name=f"N{index}", email="n@x.test", text="Текст отзыва номер", is_approved=True)

        newest = self.client.get(URL)
        oldest = self.client.get(URL, {"ordering": "created_at"})

        self.assertEqual(newest.data["pages"], 2)
        self.assertEqual(len(newest.data["results"]), 8)
        self.assertEqual(newest.data["results"][0]["name"], "N9")
        self.assertEqual(oldest.data["results"][0]["name"], "N0")

    # ---------- POST ----------

    def test_create_with_images_is_hidden_until_approved(self):
        data = {**VALID, "images": [make_image("1.jpg"), make_image("2.png", "PNG")]}

        response = self.post(data, REMOTE_ADDR="10.0.0.1")

        self.assertEqual(response.status_code, 201, response.data)
        self.assertFalse(response.data["is_approved"])
        self.assertEqual(len(response.data["images"]), 2)
        review = StoreReview.objects.get()
        self.assertEqual(review.ip_address, "10.0.0.1")
        self.assertEqual(StoreReviewImage.objects.filter(review=review).count(), 2)
        self.assertEqual(self.client.get(URL).data["count"], 0)

    def test_create_without_images_and_with_invalid_token(self):
        response = self.post(VALID, HTTP_AUTHORIZATION="Bearer expired.token.value")
        self.assertEqual(response.status_code, 201, response.data)

    def test_validation_messages(self):
        response = self.post({"name": "И", "email": "not-email", "text": "коротко"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data), {"name", "email", "text"})

    def test_rejects_too_many_images(self):
        files = [make_image(f"{i}.jpg") for i in range(limits.MAX_IMAGES + 1)]
        response = self.post({**VALID, "images": files})

        self.assertEqual(response.status_code, 400)
        self.assertIn("images", response.data)

    def test_rejects_unsupported_image_format(self):
        response = self.post({**VALID, "images": [make_image("anim.gif", "GIF")]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("images", response.data)

    def test_rejects_non_image_file(self):
        fake = SimpleUploadedFile("virus.jpg", b"not an image", content_type="image/jpeg")
        response = self.post({**VALID, "images": [fake]})

        self.assertEqual(response.status_code, 400)

    def test_rejects_too_large_image(self):
        backup = limits.MAX_IMAGE_SIZE_MB
        limits.MAX_IMAGE_SIZE_MB = 0  # har qanday fayl "katta" hisoblanadi
        try:
            response = self.post({**VALID, "images": [make_image()]})
        finally:
            limits.MAX_IMAGE_SIZE_MB = backup

        self.assertEqual(response.status_code, 400)

    def test_create_is_throttled_per_ip(self):
        allowed = int(limits.CREATE_RATE.split("/")[0])
        for _ in range(allowed):
            self.assertEqual(self.post(VALID, REMOTE_ADDR="10.0.0.2").status_code, 201)

        self.assertEqual(self.post(VALID, REMOTE_ADDR="10.0.0.2").status_code, 429)
        # Boshqa IP cheklanmaydi
        self.assertEqual(self.post(VALID, REMOTE_ADDR="10.0.0.3").status_code, 201)

    def test_update_and_delete_are_not_allowed(self):
        review = StoreReview.objects.create(name="A", email="a@x.test", text="Текст отзыва", is_approved=True)

        self.assertEqual(self.client.delete(f"{URL}{review.id}/").status_code, 404)
        self.assertEqual(self.client.put(f"{URL}{review.id}/", VALID).status_code, 404)

    def test_both_prefixes(self):
        self.assertEqual(self.client.get("/api/store-reviews/").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/store-reviews/").status_code, 200)
