from rest_framework import serializers
from product.models import Product
from .models import Cart, CartItem, Wish


class CartProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'stock', 'category_name', 'shop_name']


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = CartProductSerializer(source='product', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_detail', 'quantity', 'created_at']
        read_only_fields = ['id', 'cart', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        cart, _ = Cart.objects.get_or_create(user=user)
        product = validated_data['product']
        quantity = validated_data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cart_items', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class WishSerializer(serializers.ModelSerializer):
    product_detail = CartProductSerializer(source='product', read_only=True)

    class Meta:
        model = Wish
        fields = ['id', 'product', 'product_detail', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        wish, _ = Wish.objects.get_or_create(
            user=user,
            product=validated_data['product']
        )
        return wish
