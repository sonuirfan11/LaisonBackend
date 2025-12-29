from django.shortcuts import render

# Create your views here.
from .serializers import (
    UserLoginSerializer,
    UpdateProfileSerializer,
    AddressSerializer
)
from .models import (
    CustomUser,
    ClientProfile,
    ClientAddress
)
from rest_framework.views import APIView
from .utils import generate_otp
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .authentication import CookieJWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class UserLoginOTPView(APIView):

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            print(mobile)
            user, created = CustomUser.objects.get_or_create(mobile=mobile)
            otp = generate_otp()
            print(f"========otp======{otp}")
            user.set_otp(otp)
            return Response(
                {
                    "success": True,
                    "message": "OTP Sent Successfully!",
                    "user": {
                        "mobile": str(mobile)
                    }
                },
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginVerifyView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']

            try:
                user = CustomUser.objects.get(mobile=mobile)
            except CustomUser.DoesNotExist:
                return Response({"message": "User does not exist!"}, status=404)

            if user.is_otp_verified(otp):
                ClientProfile.objects.get_or_create(user=user)
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)

                return Response({
                    "success": True,
                    "message": "OTP verified successfully!",
                    "access": access,
                    "refresh": str(refresh),
                    "user": {
                        "mobile": str(user.mobile),
                    }
                }, status=200)

            return Response(
                {"success": False, "message": "OTP not valid or expired!"},
                status=400
            )

        return Response(serializer.errors, status=400)


class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "mobile": str(request.user.mobile),
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "gender": request.user.client_profile.gender
        })


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateProfileSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        print(f"====Error ==={serializer.errors}")
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Expect refresh token from client
            refresh_token = request.data.get("refresh")
            if refresh_token is None:
                return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist the refresh token

            return Response({"success": True, "message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(
            ClientAddress,
            pk=pk,
            user=self.request.user
        )


class AddressCreateListView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ClientAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

