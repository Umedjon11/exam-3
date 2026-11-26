from django.contrib import admin
from .models import CustomUser, Profile, DeliveryAddress, SearchHistory

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(DeliveryAddress)
admin.site.register(SearchHistory)
