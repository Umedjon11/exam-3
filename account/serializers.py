from rest_framework import serializers
from .models import CustomUser, Profile, DeliveryAddress, SearchHistory


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source='user_profile', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        return user


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'address', 'landmark', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        return DeliveryAddress.objects.create(
            user=self.context['request'].user,
            **validated_data
        )


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
