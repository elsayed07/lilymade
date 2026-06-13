from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)


class ThrottledLoginView(TokenObtainPairView):
    throttle_scope = "login"


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()
        if user is not None:
            uid, token = serializer.make_uid_token(user)
            link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            EmailMessage(
                subject="Lilymade — reset your password",
                body=(
                    "We received a request to reset your password.\n\n"
                    f"Reset it here (link valid for a limited time):\n{link}\n\n"
                    "If you didn't request this, you can safely ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            ).send(fail_silently=True)
        # Always 200 so the endpoint can't be used to enumerate accounts.
        return Response({"detail": "If that email exists, a reset link has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password updated. You can now sign in."},
            status=status.HTTP_200_OK,
        )
