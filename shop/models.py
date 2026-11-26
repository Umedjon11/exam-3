from django.db import models
from account.models import CustomUser


class Shop(models.Model):
    name = models.CharField(max_length=250)
    bio = models.TextField(null=True, blank=True)
    logo = models.CharField(max_length=250, null=True, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_shop')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
