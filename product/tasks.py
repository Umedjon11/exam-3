from celery import shared_task
from django.core.cache import cache
from django.db.models import Avg
from .models import Product
from .serializers import ProductSerializer


@shared_task
def update_product_cache():
    print('Start caching products...')
    queryset = Product.objects.select_related('category', 'shop').prefetch_related(
        'product_images', 'product_reviews__user'
    ).annotate(avg_rating_val=Avg('product_reviews__mark')).all().order_by('-created_at')
    data = ProductSerializer(queryset, many=True).data
    cache.set('product_cache', data, timeout=600)
    print('Product caching finished')
    return 'Product cache was successfully set'
