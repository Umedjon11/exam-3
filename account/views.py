from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .models import Profile, DeliveryAddress, SearchHistory
from .permissions import IsHisProfile, IsOwner
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    LogOutSerializer,
    DeliveryAddressSerializer,
    SearchHistorySerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = RegisterSerializer(request.user).data
        return Response(data=user, status=status.HTTP_200_OK)


class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsHisProfile]

    def get_object(self):
        if 'pk' in self.kwargs:
            return super().get_object()
        return self.request.user.user_profile


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsHisProfile]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=LogOutSerializer,
        responses={205: "Logged out", 400: "Validation error"}
    )
    def post(self, request):
        refresh = request.data.get('refresh')

        if not refresh:
            return Response(
                {"detail": "refresh is required!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_205_RESET_CONTENT)


class DeliveryAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DeliveryAddress.objects.none()
        return DeliveryAddress.objects.select_related('user').filter(user=self.request.user).order_by('-created_at')


class DeliveryAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DeliveryAddress.objects.none()
        return DeliveryAddress.objects.select_related('user').filter(user=self.request.user)


class SearchHistoryListView(generics.ListAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SearchHistory.objects.none()
        return SearchHistory.objects.select_related('user').filter(user=self.request.user).order_by('-created_at')


class SearchHistoryDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SearchHistory.objects.none()
        return SearchHistory.objects.select_related('user').filter(user=self.request.user)
