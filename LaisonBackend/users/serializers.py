from rest_framework import serializers
from rest_framework.views import APIView
from .models import (
    CustomUser,
    ClientProfile,
    ClientAddress
)


class UserLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=15, )
    otp = serializers.CharField(max_length=6, required=False, allow_blank=True)


class UpdateProfileSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source="client_profile.gender", required=False)
    #dob = serializers.DateField(source="client_profile.dob", required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'gender')

    def update(self, instance, validated_data):
        client_profile_data = validated_data.pop('client_profile', {})

        # update user
        instance = super().update(instance, validated_data)

        # update client profile
        profile = instance.client_profile
        for attr, value in client_profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAddress
        fields = '__all__'
        read_only_fields = ['user']


