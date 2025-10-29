from rest_framework import serializers
from rest_framework.views import APIView
from .models import CustomUser


class UserLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15,)
    otp = serializers.CharField(max_length=6, required=False, allow_blank=True)


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')