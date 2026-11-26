from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import CustomUser
from shop.models import Shop


class Category(models.Model):
    name = models.CharField(max_length=250)
    logo = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_products')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_products')
    stock = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.title} - {self.image}'


class Review(models.Model):
    mark = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.title} ({self.mark})'
