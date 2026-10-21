from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.magazin.models import Order
from api.payments.views import make_sign


class PaymentCallbackTests(TestCase):
    secret = "test-callback-secret"

    def setUp(self):
        self.client = APIClient()
        self.order = Order.objects.create(
            number="callback-test-order",
            status="pending",
            subtotal=Decimal("25.00"),
            total=Decimal("25.00"),
        )

    @override_settings(FHP_SERVICE_SECRET_KEY="test-callback-secret")
    def test_prepare_callback_uses_order_total(self):
        payload = {
            "click_trans_id": "transaction-1",
            "service_id": "1",
            "merchant_trans_id": str(self.order.pk),
            "amount": "25.00",
            "action": "0",
            "sign_time": "2026-10-21 12:00:00",
        }
        payload["sign_string"] = make_sign(
            payload["click_trans_id"],
            payload["service_id"],
            self.secret,
            payload["merchant_trans_id"],
            payload["amount"],
            payload["action"],
            payload["sign_time"],
        )

        response = self.client.post(
            "/api/payments/prepare/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["error"], 0)
        self.assertEqual(response.data["merchant_prepare_id"], self.order.pk)

    @override_settings(FHP_SERVICE_SECRET_KEY="test-callback-secret")
    def test_complete_callback_marks_order_paid(self):
        payload = {
            "click_trans_id": "transaction-2",
            "service_id": "1",
            "merchant_trans_id": str(self.order.pk),
            "merchant_prepare_id": str(self.order.pk),
            "amount": "25.00",
            "action": "1",
            "sign_time": "2026-10-21 12:01:00",
            "error": "0",
        }
        payload["sign_string"] = make_sign(
            payload["click_trans_id"],
            payload["service_id"],
            self.secret,
            payload["merchant_trans_id"],
            payload["merchant_prepare_id"],
            payload["amount"],
            payload["action"],
            payload["sign_time"],
        )

        response = self.client.post(
            "/api/payments/complete/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["error"], 0)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "paid")


class PaymentLoginRouteTests(TestCase):
    @patch("api.payments.views.requests.post")
    def test_post_without_trailing_slash_is_not_redirected(self, post):
        upstream_response = Mock()
        upstream_response.json.return_value = {"message": "Login response"}
        upstream_response.status_code = 200
        post.return_value = upstream_response

        response = self.client.post(
            "/api/payments/login",
            {"email": "user@example.com", "password": "not-a-real-password"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Login response"})
        self.assertTrue(
            post.call_args.args[0].endswith("/api/auth/login/"),
        )


class CardPaymentProxyTests(TestCase):
    @override_settings(FHP_BASE_URL="http://fintech.example", FHP_SERVICE_ID=1)
    @patch("api.payments.clients.requests.request")
    def test_card_payment_uses_upstream_api_prefix(self, upstream_request):
        upstream_response = Mock()
        upstream_response.json.return_value = {"success": True}
        upstream_response.status_code = 200
        upstream_request.return_value = upstream_response

        response = APIClient().post(
            "/api/payments/card/payment/",
            {"card_token": "test-token"},
            format="json",
            HTTP_AUTHORIZATION="Bearer upstream-token",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"success": True})
        self.assertEqual(
            upstream_request.call_args.kwargs["url"],
            "http://fintech.example/api/v2/merchant/card_token/payment",
        )
        self.assertEqual(
            upstream_request.call_args.kwargs["headers"]["Authorization"],
            "Bearer upstream-token",
        )
