from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView

from myproject.serializers import CustomTokenObtainPairSerializer



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