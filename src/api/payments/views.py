# import hashlib, hmac, json
# from decimal import Decimal
# from apps.users.models import Order

# import requests
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from api.payments.clients import FintechhubClient
# Order importini hozirgi views.py dagidek qoldiring (from apps.... import Order)
import hashlib
import hmac
import json
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.magazin.models import Order

from api.payments.clients import FintechhubClient
from drf_spectacular.utils import OpenApiResponse, extend_schema


def _upstream_non_json_error(response):
    response_text = response.text.lower()
    if (
        "access to arbitrary websites is not available from free accounts"
        in response_text
        and "pythonanywhere.com/whitelist" in response_text
    ):
        message = (
            "PythonAnywhere blocked this server's outbound request. "
            "Ask PythonAnywhere to allowlist the payment provider's official "
            "API hostname, or deploy on a host that permits outbound access."
        )
    else:
        message = "Payment provider returned a non-JSON response."

    return {
        "error": message,
        "upstream_status": response.status_code,
        "upstream_content_type": response.headers.get("Content-Type", ""),
    }


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                },
            },
            "required": [
                "email",
                "password",
            ],
        },
    },
    responses={
        200: OpenApiResponse(
            description="FintechHub login response.",
        ),
        400: OpenApiResponse(
            description="Invalid login data.",
        ),
        502: OpenApiResponse(
            description="FintechHub connection error.",
        ),
    },
    tags=["Payments Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    return _forward_auth(
        request,
        "/api/auth/login/",
    )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                },
                "full_name": {
                    "type": "string",
                },
            },
            "required": [
                "email",
                "password",
            ],
        },
    },
    responses={
        201: OpenApiResponse(
            description="FintechHub registration response.",
        ),
        400: OpenApiResponse(
            description="Invalid registration data.",
        ),
        502: OpenApiResponse(
            description="FintechHub connection error.",
        ),
    },
    tags=["Payments Authentication"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    return _forward_auth(
        request,
        "/api/auth/register/",
    )



# ---------- LOGIN / REGISTER (ustoz usuli) ----------
def _forward_auth(request, path):
    if request.method != "POST":
        return JsonResponse({"error": "Faqat POST"}, status=405)
    try:
        data = json.loads(request.body) if request.body else request.POST.dict()
    except ValueError:
        return JsonResponse({"error": "Noto'g'ri JSON"}, status=400)
    try:
        base_url = settings.FHP_BASE_URL.rstrip("/")
        resp = requests.post(f"{base_url}{path}", json=data, timeout=20)
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Fintechhub javob bermadi"}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=502)
    try:
        return JsonResponse(resp.json(), status=resp.status_code, safe=False)
    except ValueError:
        return JsonResponse(_upstream_non_json_error(resp), status=502)


# @csrf_exempt
# def login(request):
#     return _forward_auth(request, "/api/auth/login/")


# @csrf_exempt
# def register(request):
#     return _forward_auth(request, "/api/auth/register/")


# ---------- TO'LOV PROXY ----------
class FintechProxy(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    path = None

    def post(self, request):
        body = {k: v for k, v in request.data.items()}
        body["service_id"] = int(settings.FHP_SERVICE_ID)
        try:
            resp = FintechhubClient().request(
                "POST",
                self.path,
                json_data=body,
                authorization=request.headers.get("Authorization"),
            )
        except requests.exceptions.Timeout:
            return Response({"error": "Fintechhub javob bermadi (timeout)"}, status=504)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=502)
        try:
            data = resp.json()
        except ValueError:
            return Response(_upstream_non_json_error(resp), status=502)
        return Response(data, status=resp.status_code)


class PayInitView(FintechProxy):
    path = "/api/v2/pay/init"

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "merchant_trans_id": {"type": "string"},
                    "user_id": {"type": "integer"},
                },
                "required": ["amount", "merchant_trans_id"],
            },
        },
        responses={
            200: OpenApiResponse(description="Payment init response."),
            502: OpenApiResponse(description="FintechHub connection error."),
        },
        tags=["Payments"],
    )
    def post(self, request):
        return super().post(request)


class CardRequestView(FintechProxy):
    path = "/api/v2/merchant/card_token/request"

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "card_number": {"type": "string"},
                    "expiry": {"type": "string"},
                    "amount": {"type": "number"},
                },
                "required": ["card_number", "expiry", "amount"],
            },
        },
        responses={
            200: OpenApiResponse(description="Card token request response."),
            502: OpenApiResponse(description="FintechHub connection error."),
        },
        tags=["Payments"],
    )
    def post(self, request):
        return super().post(request)


class CardVerifyView(FintechProxy):
    path = "/api/v2/merchant/card_token/verify"

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "card_token": {"type": "string"},
                    "otp": {"type": "string"},
                },
                "required": ["card_token", "otp"],
            },
        },
        responses={
            200: OpenApiResponse(description="Card verification response."),
            502: OpenApiResponse(description="FintechHub connection error."),
        },
        tags=["Payments"],
    )
    def post(self, request):
        return super().post(request)


class CardPaymentView(FintechProxy):
    path = "/api/v2/merchant/card_token/payment"

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "card_token": {"type": "string"},
                    "amount": {"type": "number"},
                },
                "required": ["card_token", "amount"],
            },
        },
        responses={
            200: OpenApiResponse(description="Card payment response."),
            502: OpenApiResponse(description="FintechHub connection error."),
        },
        tags=["Payments"],
    )
    def post(self, request):
        return super().post(request)


# ---------- CALLBACKLAR (Fintechhub chaqiradi) ----------
def make_sign(*parts):
    return hashlib.md5("".join(str(p) for p in parts).encode()).hexdigest()


def _get_service_secret():
    if not settings.FHP_SERVICE_SECRET_KEY:
        raise ImproperlyConfigured(
            "FHP_SERVICE_SECRET_KEY must be configured to verify payment callbacks."
        )
    return settings.FHP_SERVICE_SECRET_KEY


class PrepareCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "click_trans_id": {"type": "string"},
                    "service_id": {"type": "integer"},
                    "merchant_trans_id": {"type": "string"},
                    "amount": {"type": "number"},
                    "action": {"type": "integer"},
                    "sign_time": {"type": "string"},
                    "sign_string": {"type": "string"},
                },
                "required": ["click_trans_id", "service_id", "merchant_trans_id", "amount", "action", "sign_time", "sign_string"],
            },
        },
        responses={
            200: OpenApiResponse(description="Prepare callback response."),
            400: OpenApiResponse(description="Invalid request data."),
        },
        tags=["Payment Callbacks"],
    )
    def post(self, request):
        d = request.data
        try:
            click_trans_id = d.get("click_trans_id")
            service_id = d.get("service_id")
            merchant_trans_id = d.get("merchant_trans_id")
            amount = d.get("amount")
            action = d.get("action")
            sign_time = d.get("sign_time")
            sign_string = d.get("sign_string")

            if not all([click_trans_id, merchant_trans_id, amount is not None, action is not None, sign_time, sign_string]):
                return Response({"error": -3, "error_note": "Missing required fields"}, status=400)

            expected = make_sign(
                click_trans_id, service_id,
                _get_service_secret(), merchant_trans_id,
                amount, action, sign_time,
            )
            if not hmac.compare_digest(expected, str(sign_string)):
                return Response({"error": -1, "error_note": "SIGN CHECK FAILED"}, status=400)

            try:
                order = Order.objects.get(id=merchant_trans_id)
            except (Order.DoesNotExist, ValueError, TypeError):
                return Response({"error": -5, "error_note": "Order not found"}, status=400)

            try:
                if Decimal(str(amount)) != Decimal(str(order.total)):
                    return Response({"error": -2, "error_note": "Incorrect amount"}, status=400)
            except (InvalidOperation, ValueError, TypeError):
                return Response({"error": -2, "error_note": "Incorrect amount"}, status=400)

            return Response({
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_prepare_id": order.id,
                "error": 0, "error_note": "Success",
            })
        except Exception:
            return Response({"error": -1, "error_note": "Invalid request"}, status=400)


class CompleteCallbackView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "click_trans_id": {"type": "string"},
                    "service_id": {"type": "integer"},
                    "merchant_trans_id": {"type": "string"},
                    "merchant_prepare_id": {"type": "integer"},
                    "amount": {"type": "number"},
                    "action": {"type": "integer"},
                    "sign_time": {"type": "string"},
                    "sign_string": {"type": "string"},
                    "error": {"type": "string"},
                },
                "required": ["click_trans_id", "service_id", "merchant_trans_id", "merchant_prepare_id", "amount", "action", "sign_time", "sign_string"],
            },
        },
        responses={
            200: OpenApiResponse(description="Complete callback response."),
            400: OpenApiResponse(description="Invalid request data."),
        },
        tags=["Payment Callbacks"],
    )
    def post(self, request):
        d = request.data
        try:
            click_trans_id = d.get("click_trans_id")
            service_id = d.get("service_id")
            merchant_trans_id = d.get("merchant_trans_id")
            merchant_prepare_id = d.get("merchant_prepare_id")
            amount = d.get("amount")
            action = d.get("action")
            sign_time = d.get("sign_time")
            sign_string = d.get("sign_string")

            if not all([click_trans_id, merchant_trans_id, merchant_prepare_id is not None, amount is not None, action is not None, sign_time, sign_string]):
                return Response({"error": -3, "error_note": "Missing required fields"}, status=400)

            expected = make_sign(
                click_trans_id, service_id,
                _get_service_secret(), merchant_trans_id,
                merchant_prepare_id, amount,
                action, sign_time,
            )
            if not hmac.compare_digest(expected, str(sign_string)):
                return Response({"error": -1, "error_note": "SIGN CHECK FAILED"}, status=400)

            try:
                order = Order.objects.get(id=merchant_trans_id)
            except (Order.DoesNotExist, ValueError, TypeError):
                return Response({"error": -5, "error_note": "Order not found"}, status=400)

            try:
                if str(d.get("error")) == "0":
                    order.status = "paid"
                    order.save()
            except Exception:
                return Response({"error": -1, "error_note": "Failed to update order"}, status=400)

            return Response({
                "click_trans_id": click_trans_id,
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": order.id,
                "error": 0, "error_note": "Success",
            })
        except Exception:
            return Response({"error": -1, "error_note": "Invalid request"}, status=400)
