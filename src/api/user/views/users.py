from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings

from apps.users.models import User, Address
from ..serializers.users_serializers import (
    RegisterSerializer,
    LoginSerializer,
    RequestPasswordResetSerializer,
    ConfirmPasswordResetSerializer,
    AddressSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)

password_reset_token = PasswordResetTokenGenerator()


# =============================================================
# TASK: REGISTER (AUTHENTICATION)
# =============================================================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()  # is_active=True is set in the serializer now

        return Response(
            {"message": "User registered successfully.", "email": user.email},
            status=status.HTTP_201_CREATED,
        )


# =============================================================
# TASK: LOGIN
# =============================================================
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom Login View using JWT with email-based authentication."""

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response(
                {"error": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
            },
        }, status=status.HTTP_200_OK)


# =============================================================
# TASK: LOGOUT
# =============================================================
class LogoutView(APIView):
    """
    Custom Logout View.
    It blacklists the refresh token so it cannot be reused.
    Requires `rest_framework_simplejwt.token_blacklist` in INSTALLED_APPS.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# =============================================================
# TASK: FORGET PASSWORD
# =============================================================
class RequestPasswordResetView(APIView):
    """Step 1: Generates a signed reset link/token and emails it."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)

            send_mail(
                subject='Password Reset Request',
                message=f'Use this token to reset your password: {uid}:{token}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        # Always return 200 even if the email doesn't exist
        # (Security: prevents email enumeration)
        return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


class ConfirmPasswordResetView(APIView):
    """Step 2: Validates the token and updates the password."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']

        try:
            uidb64, token = raw_token.split(':', 1)
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.filter(pk=uid).first()
        except (ValueError, TypeError):
            user = None
            token = None

        if not user or not password_reset_token.check_token(user, token):
            return Response({"error": "Invalid or expired reset token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


# =============================================================
# TASK: USER PROFILE
# =============================================================
class UserProfileView(APIView):
    """Returns the authenticated user's profile with nested addresses."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# =============================================================
# TASK: USER DELIVERY ADDRESSES (CRUD)
# =============================================================
class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for the user's delivery addresses.
    - Only the owner can see/manage their addresses.
    - Automatically links new addresses to the logged-in user.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# =============================================================
# TASK: USER PROFIL UPDATE PASSWORD (2026-08-22)
# =============================================================
class ChangePasswordView(APIView):
    """
    Allows an authenticated user to change their password.
    The user must provide the current password for security.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not request.user.check_password(old_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )