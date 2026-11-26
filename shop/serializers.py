from django.db.models import Avg
from rest_framework import serializers
from .models import Shop


class ShopSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='user.username', read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ['id', 'name', 'bio', 'logo', 'user', 'owner_username', 'rating', 'created_at']
        read_only_fields = ['id', 'user', 'owner_username', 'rating', 'created_at']

    def get_rating(self, obj):
        if hasattr(obj, 'rating_val'):
            return round(obj.rating_val, 2) if obj.rating_val is not None else 0
        avg = obj.shop_products.aggregate(avg=Avg('product_reviews__mark'))['avg']
        return round(avg, 2) if avg is not None else 0

    def create(self, validated_data):
        user = self.context['request'].user
        if Shop.objects.filter(user=user).exists():
            raise serializers.ValidationError({"detail": "You already have a shop."})
        return Shop.objects.create(
            user=user,
            **validated_data
        )
