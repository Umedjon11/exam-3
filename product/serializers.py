from django.db.models import Avg
from rest_framework import serializers
from shop.models import Shop
from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'logo', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'logo']


class ProductShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'logo']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_product(self, product):
        request = self.context.get('request')
        if request and product.shop.user != request.user:
            raise serializers.ValidationError("You can only add images to your own shop's products.")
        return product


class ProductImageShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'mark', 'comment', 'user', 'username', 'product', 'created_at']
        read_only_fields = ['id', 'user', 'username', 'created_at']

    def create(self, validated_data):
        return Review.objects.create(
            user=self.context['request'].user,
            **validated_data
        )


class ProductReviewShortSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'mark', 'comment', 'user', 'username', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_detail = ProductCategorySerializer(source='category', read_only=True)
    shop_detail = ProductShopSerializer(source='shop', read_only=True)
    images = ProductImageShortSerializer(source='product_images', many=True, read_only=True)
    reviews = ProductReviewShortSerializer(source='product_reviews', many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'category',
            'category_detail',
            'shop',
            'shop_detail',
            'stock',
            'avg_rating',
            'images',
            'reviews',
            'updated_at',
            'created_at',
        ]
        read_only_fields = ['id', 'updated_at', 'created_at']

    def get_avg_rating(self, obj):
        if hasattr(obj, 'avg_rating_val'):
            return round(obj.avg_rating_val, 2) if obj.avg_rating_val is not None else 0
        avg = obj.product_reviews.aggregate(avg=Avg('mark'))['avg']
        return round(avg, 2) if avg is not None else 0

    def validate_shop(self, shop):
        request = self.context.get('request')
        if request and shop.user != request.user:
            raise serializers.ValidationError("You can only add products to your own shop.")
        return shop
