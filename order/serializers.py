from django.core.cache import cache
from django.db import transaction
from rest_framework import serializers
from account.models import DeliveryAddress
from cart.models import Cart
from product.models import Product
from .models import Order, OrderItem


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['id', 'address', 'landmark']


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderSerializer(serializers.ModelSerializer):
    address_detail = OrderAddressSerializer(source='address', read_only=True)
    items = OrderItemSerializer(source='order_items', many=True, read_only=True)
    order_items_input = OrderItemCreateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'address', 'address_detail', 'comment', 'status', 'items', 'order_items_input', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'created_at']

    def validate_address(self, address):
        request = self.context.get('request')
        if address and request and address.user != request.user:
            raise serializers.ValidationError("You can only use your own delivery address.")
        return address

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('order_items_input', None)

        with transaction.atomic():
            if items_data:
                items_to_order = [
                    (item['product'], item.get('quantity', 1))
                    for item in items_data
                ]
                cart = None
            else:
                cart = Cart.objects.filter(user=user).first()
                if not cart or not cart.cart_items.exists():
                    raise serializers.ValidationError({"detail": "Cart is empty or items are required."})
                items_to_order = [
                    (cart_item.product_id, cart_item.quantity)
                    for cart_item in cart.cart_items.all()
                ]

            order = Order.objects.create(user=user, **validated_data)

            for product_id, quantity in items_to_order:
                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError({"detail": f"Product {product_id} not found."})

                if product.stock < quantity:
                    raise serializers.ValidationError(
                        {"detail": f"Not enough stock for {product.title}. Available: {product.stock}"}
                    )

                product.stock -= quantity
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )

            if cart:
                cart.cart_items.all().delete()

        cache.delete('product_cache')
        return order
