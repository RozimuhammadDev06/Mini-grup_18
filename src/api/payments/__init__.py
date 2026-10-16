from django.urls import path, include

path(
    "api/payments/",
    include("api.payments.urls"),
),
