from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        # Try to get user by username first, then email
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise serializers.ValidationError("No user found with this username/email.")

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect credentials.")

        # Replace 'username' in attrs with actual username to let parent class handle token creation
        attrs['username'] = user.username

        return super().validate(attrs)
