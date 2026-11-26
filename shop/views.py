from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, permissions
from .models import Shop
from .serializers import ShopSerializer
from .permissions import IsShopOwnerOrReadOnly


class ShopListCreateView(generics.ListCreateAPIView):
    queryset = Shop.objects.select_related('user').annotate(
        rating_val=Avg('shop_products__product_reviews__mark')
    ).all().order_by('-created_at')
    serializer_class = ShopSerializer
    permission_classes = [IsShopOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'bio']


class ShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shop.objects.select_related('user').annotate(
        rating_val=Avg('shop_products__product_reviews__mark')
    ).all()
    serializer_class = ShopSerializer
    permission_classes = [IsShopOwnerOrReadOnly]


class MyShopView(generics.RetrieveAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            Shop.objects.select_related('user').annotate(
                rating_val=Avg('shop_products__product_reviews__mark')
            ),
            user=self.request.user
        )
