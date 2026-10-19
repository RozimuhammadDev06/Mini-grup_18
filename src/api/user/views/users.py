from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
 )

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
)

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.users.models import Address, User

from ..serializers.users_serializers import (
    AddressSerializer,
    ChangePasswordSerializer,
    ConfirmPasswordResetSerializer,
    LoginSerializer,
    RegisterSerializer,
    RequestPasswordResetSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)


password_reset_token = PasswordResetTokenGenerator()


# =============================================================
# REGISTER
# =============================================================

class RegisterView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User registered successfully.",
            ),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


# =============================================================
# LOGIN
# =============================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [
        permissions.AllowAny,
    ]

    

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="JWT tokens returned successfully.",
            ),
            401: OpenApiResponse(
                description="Invalid email or password.",
            ),
            403: OpenApiResponse(
                description="The account is inactive.",
            ),
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User.objects.filter(
            email=email,
        ).first()

        if not user or not user.check_password(password):
            return Response(
                {
                    "error": "Invalid email or password",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {
                    "error": "This account is inactive.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            {
                "access": access_token,
                "refresh": refresh_token,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                },
            },
            status=status.HTTP_200_OK,
        )


# =============================================================
# TOKEN REFRESH
# =============================================================

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [
        permissions.AllowAny,
    ]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Access token refreshed successfully.",
            ),
        },
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(
            request,
            *args,
            **kwargs,
        )


# =============================================================
# LOGOUT
# =============================================================

class LogoutView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refresh": {
                        "type": "string",
                        "description": "JWT refresh token.",
                    },
                },
                "required": ["refresh"],
            },
        },
        responses={
            205: OpenApiResponse(
                description="Logout completed successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid or expired refresh token.",
            ),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        refresh_token = request.data.get(
            "refresh",
        )

        if not refresh_token:
            return Response(
                {
                    "error": "Refresh token is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(
                refresh_token,
            )
            token.blacklist()

        except Exception:
            return Response(
                {
                    "error": "Invalid or expired refresh token.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            status=status.HTTP_205_RESET_CONTENT,
        )


# =============================================================
# REQUEST PASSWORD RESET
# =============================================================

class RequestPasswordResetView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    @extend_schema(
        request=RequestPasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset request processed.",
            ),
        },
        tags=["Password"],
    )
    def post(self, request):
        serializer = RequestPasswordResetSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email=email,
        ).first()

        if user:
            uid = urlsafe_base64_encode(
                force_bytes(user.pk),
            )

            token = password_reset_token.make_token(
                user,
            )

            send_mail(
                subject="Password Reset Request",
                message=(
                    "Use this token to reset your password: "
                    f"{uid}:{token}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        # Do not reveal whether the email exists.
        return Response(
            {
                "message": (
                    "If the email exists, "
                    "a reset link has been sent."
                ),
            },
            status=status.HTTP_200_OK,
        )


# =============================================================
# CONFIRM PASSWORD RESET
# =============================================================

class ConfirmPasswordResetView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    @extend_schema(
        request=ConfirmPasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                description="Password updated successfully.",
            ),
            400: OpenApiResponse(
                description="Invalid or expired reset token.",
            ),
        },
        tags=["Password"],
    )
    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        raw_token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]

        try:
            uidb64, token = raw_token.split(
                ":",
                1,
            )

            uid = force_str(
                urlsafe_base64_decode(
                    uidb64,
                ),
            )

            user = User.objects.filter(
                pk=uid,
            ).first()

        except (
            ValueError,
            TypeError,
        ):
            user = None
            token = None

        if not user or not password_reset_token.check_token(
            user,
            token,
        ):
            return Response(
                {
                    "error": "Invalid or expired reset token.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(
            new_password,
        )
        user.save(
            update_fields=["password"],
        )

        return Response(
            {
                "message": "Password updated successfully.",
            },
            status=status.HTTP_200_OK,
        )


# =============================================================
# USER PROFILE
# =============================================================

class UserProfileView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        responses={
            200: UserProfileSerializer,
        },
        tags=["Users"],
    )
    def get(self, request):
        serializer = UserProfileSerializer(
            request.user,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=UserUpdateSerializer,
        responses={
            200: UserProfileSerializer,
        },
        tags=["Users"],
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save()

        response_serializer = UserProfileSerializer(
            request.user,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


# =============================================================
# USER ADDRESSES
# =============================================================

class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for addresses. Authenticated users see only their own addresses;
    unauthenticated users can create an address (user left null).
    """

    serializer_class = AddressSerializer
    permission_classes = [
        permissions.AllowAny,
    ]

    def get_queryset(self):
        if getattr(
            self,
            "swagger_fake_view",
            False,
        ):
            return Address.objects.none()

        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated:
            return Address.objects.none()

        return Address.objects.filter(
            user=user,
        )

    def perform_create(self, serializer):
        user = getattr(self.request, "user", None)
        if user is not None and user.is_authenticated:
            serializer.save(user=user)
        else:
            serializer.save(user=None)


# =============================================================
# CHANGE PASSWORD
# =============================================================

class ChangePasswordView(APIView):
  
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password changed successfully.",
            ),
            400: OpenApiResponse(
                description="Current password is incorrect.",
            ),
        },
        tags=["Password"],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        old_password = serializer.validated_data[
            "old_password"
        ]
        new_password = serializer.validated_data[
            "new_password"
        ]

        if not request.user.check_password(
            old_password,
        ):
            return Response(
                {
                    "error": (
                        "Current password is incorrect."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(
            new_password,
        )
        request.user.save(
            update_fields=["password"],
        )

        return Response(
            {
                "message": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )
