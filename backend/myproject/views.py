from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView

from myproject.serializers import CustomTokenObtainPairSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        password= request.data.get("password1")
        password2 = request.data.get("password2")
        email = request.data.get("email")
        username = request.data.get("mobile")

        if not email or not password or not username:
            return Response({"error": "Email and password and mobile are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if password != password2:  
            return Response({"error": "password and password2 are not equal. "}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            return Response({"error": "Email  or Mobile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "User registered successfully.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # To avoid revealing whether an email exists, return success anyway
            return Response({'message': 'If an account with that email exists, a password reset email has been sent.'}, status=status.HTTP_200_OK)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build reset url (frontend should handle the route). Provide uid and token.
        reset_url = f"{request.scheme}://{request.get_host()}/reset-password/?uid={uid}&token={token}"

        subject = 'Password reset request'
        message = render_to_string('password_reset_email.txt', {'user': user, 'reset_url': reset_url})

        send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'), [user.email], fail_silently=False)

        return Response({'message': 'If an account with that email exists, a password reset email has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid') or request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uidb64 or not token or not new_password:
            return Response({'error': 'uid, token and new_password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid uid.'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)