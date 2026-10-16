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

from .views import (
    login,
    register,
    PayInitView,
    CardRequestView,
    CardVerifyView,
    CardPaymentView,
    PrepareCallbackView,
    CompleteCallbackView,
)

urlpatterns = [
    path("login/", login, name="payment-login"),
    path("register/", register, name="payment-register"),

    path("pay/init/", PayInitView.as_view(), name="pay-init"),
    path("card/request/", CardRequestView.as_view(), name="card-request"),
    path("card/verify/", CardVerifyView.as_view(), name="card-verify"),
    path("card/payment/", CardPaymentView.as_view(), name="card-payment"),

    path("prepare/", PrepareCallbackView.as_view(), name="payment-prepare"),
    path("complete/", CompleteCallbackView.as_view(), name="payment-complete"),
]