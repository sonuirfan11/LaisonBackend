from django.shortcuts import render

# Create your views here.
from .serializers import UserLoginSerializer,UpdateProfileSerializer
from .models import CustomUser
from rest_framework.views import APIView
from .utils import generate_otp
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated


class UserLoginOTPView(APIView):

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = CustomUser.objects.get_or_create(mobile=mobile)
            user.set_otp(generate_otp())
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
                return Response(
                    {"message": "User does not exist!"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if user.is_otp_verified(otp):
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "success": True,
                        "message": "OTP verified successfully!",
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "mobile": str(user.mobile),
                        }
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"success": False, "message": "OTP not valid or expired!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "mobile": str(request.user.mobile),
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email
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


