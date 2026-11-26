from django.db import models
from account.models import CustomUser
from product.models import Product


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.cart.user.username} - {self.product.title} x{self.quantity}'


class Wish(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_wishes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_wishes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.title}'
