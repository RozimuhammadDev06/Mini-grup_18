"""
Fixed and complete users/views.py for 'СтройОптТорг'

What was wrong / missing in the original file (fixed here):
1. `request.user.username` in CustomTokenObtainPairView — the new User model
   has no username field (email login). Also, `request.user` is AnonymousUser
   at login time, so accessing it before login raises errors. Fixed.
2. The original file only had Login, Logout, and Password Reset views. The
   Register, VerifyCode, and ResendCode views from the auth tasks were missing,
   so the endpoints in urls.py would crash. Added them, wired to the OTP model.
3. Login now blocks unverified emails (is_email_verified check).
4. Password reset now uses the UserOTPVerifications table from your models.py
   (matching your OTP flow) instead of the old password_reset_token field.
5. AddressViewSet from the delivery address task is included so addresses CRUD works.
6. All views use the local serializers instead of raw request.data where useful.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings

from apps.users.models import User, UserOTPVerifications, Address
from ..serializers.users_serializers import (
    RegisterSerializer,
    VerifyCodeSerializer,
    ResendCodeSerializer,
    LoginSerializer,
    RequestPasswordResetSerializer,
    ConfirmPasswordResetSerializer,
    AddressSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)


# =============================================================
# TASK: REGISTER (AUTHENTICATION)
# =============================================================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Create an OTP record, generate the code and email it
        otp = UserOTPVerifications.objects.create(user=user, for_forget_password=False)
        code = otp.generate_code()

        send_mail(
            subject='Verify your email',
            message=f'Your verification code is: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "User registered. Please verify your email.", "email": user.email},
            status=status.HTTP_201_CREATED,
        )


# =============================================================
# TASK: VERIFY CODE
# =============================================================
class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_email_verified:
            return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)

        # Find the newest (non-expired) OTP for this user
        now = __import__('django.utils.timezone', fromlist=['now']).now()
        otp = UserOTPVerifications.objects.filter(
            user=user, for_forget_password=False
        ).order_by('-created_at').first()

        if not otp:
            return Response({"error": "No verification code found. Please resend."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.expired_at < now:
            return Response({"error": "Code expired. Please resend."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.attapts >= 5:
            return Response({"error": "Too many attempts. Please request a new code."}, status=status.HTTP_403_FORBIDDEN)

        if str(otp.code) != str(code):
            otp.attapts += 1
            otp.save(update_fields=['attapts'])
            remaining = 5 - otp.attapts
            return Response(
                {"error": f"Invalid code. {remaining} attempts remaining."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Code is valid
        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=['is_email_verified', 'is_active'])
        otp.for_forget_password_verified = True
        otp.save(update_fields=['for_forget_password_verified'])

        return Response({
            "message": "Email verified successfully!",
            "tokens": user.generate_jwt_token(),
        }, status=status.HTTP_200_OK)


# =============================================================
# TASK: RESEND VERIFY CODE
# =============================================================
class ResendCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_email_verified:
            return Response({"message": "Email already verified"}, status=status.HTTP_200_OK)

        otp = UserOTPVerifications.objects.create(user=user, for_forget_password=False)
        code = otp.generate_code()

        send_mail(
            subject='New Verification Code',
            message=f'Your new verification code is: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "New verification code sent"}, status=status.HTTP_200_OK)


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

        if not user.is_email_verified:
            return Response(
                {"error": "Please verify your email before logging in."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = user.generate_jwt_token()
        return Response({
            'refresh_token': tokens['refresh_token'],
            'access_token': tokens['access_token'],
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
    """Step 1: Generates an OTP and sends it to the user's email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            otp = UserOTPVerifications.objects.create(user=user, for_forget_password=True)
            code = otp.generate_code()

            send_mail(
                subject='Password Reset Code',
                message=f'Your password reset code is: {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        # Always return 200 even if the email doesn't exist
        # (Security: prevents email enumeration)
        return Response({"message": "If the email exists, a reset code has been sent."}, status=status.HTTP_200_OK)


class ConfirmPasswordResetView(APIView):
    """Step 2: Validates the OTP and updates the password."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['token']
        new_password = serializer.validated_data['password']

        if not code:
            return Response({"error": "Reset code is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the newest unverified forget-password OTP with this code
        otp = UserOTPVerifications.objects.filter(
            code=str(code), for_forget_password=True
        ).order_by('-created_at').first()

        if not otp:
            return Response({"error": "Invalid or used reset code"}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        if otp.expired_at < timezone.now():
            return Response({"error": "Reset code expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        if otp.for_forget_password_verified:
            return Response({"error": "This code has already been used"}, status=status.HTTP_400_BAD_REQUEST)

        user = otp.user
        user.set_password(new_password)
        user.save(update_fields=['password'])

        otp.for_forget_password_verified = True
        otp.save(update_fields=['for_forget_password_verified'])

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
