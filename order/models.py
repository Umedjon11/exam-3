from django.db import models
from account.models import CustomUser, DeliveryAddress
from product.models import Product


class Order(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_orders')
    address = models.ForeignKey(
        DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='address_orders'
    )
    comment = models.TextField(null=True, blank=True)
    status = models.CharField(choices=STATUS, default='pending', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_order_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.order.id} - {self.product.title} x{self.quantity}'
