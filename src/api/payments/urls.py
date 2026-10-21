# from django.urls import path
# from . import views

# urlpatterns = [
#     path('login/', views.login),
#     path('register/', views.register),
#     path('pay/init/', views.PayInitView.as_view()),
#     path('card/request/', views.CardRequestView.as_view()),
#     path('card/verify/', views.CardVerifyView.as_view()),
#     path('card/payment/', views.CardPaymentView.as_view()),
#     path('prepare/', views.PrepareCallbackView.as_view()),
#     path('complete/', views.CompleteCallbackView.as_view()),
# ]


from django.urls import path

from . import views


app_name = "payments"


urlpatterns = [
    path(
        "login",
        views.login,
        name="payment-login-no-slash",
    ),
    path(
        "login/",
        views.login,
        name="payment-login",
     ),
    path(
        "register/",
        views.register,
        name="payment-register",
    ),
    path(
        "pay/init/",
        views.PayInitView.as_view(),
        name="payment-init",
    ),
    path(
        "card/request/",
        views.CardRequestView.as_view(),
        name="card-request",
    ),
    path(
        "card/verify/",
        views.CardVerifyView.as_view(),
        name="card-verify",
    ),
    path(
        "card/payment/",
        views.CardPaymentView.as_view(),
        name="card-payment",
    ),
    path(
        "prepare/",
        views.PrepareCallbackView.as_view(),
        name="payment-prepare",
    ),
    path(
        "complete/",
        views.CompleteCallbackView.as_view(),
        name="payment-complete",
    ),
]
