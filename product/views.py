from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Count, Q
from rest_framework import generics, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from account.models import CustomUser, SearchHistory
from order.models import Order
from shop.models import Shop
from .models import Category, Product, ProductImage, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    ReviewSerializer,
)
from .permissions import (
    IsProductShopOwnerOrReadOnly,
    IsImageShopOwnerOrReadOnly,
    IsReviewOwnerOrReadOnly,
)
from .tasks import update_product_cache


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('-created_at')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related('category', 'shop').prefetch_related(
        'product_images', 'product_reviews__user'
    ).annotate(avg_rating_val=Avg('product_reviews__mark')).all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsProductShopOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        shop_id = self.request.query_params.get('shop')
        search_query = self.request.query_params.get('search')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        if search_query and self.request.user.is_authenticated:
            SearchHistory.objects.create(user=self.request.user, query=search_query)

        return queryset

    def list(self, request, *args, **kwargs):
        has_filters = any(
            k in request.query_params for k in ('category', 'shop', 'search', 'page', 'page_size')
        )
        if not has_filters:
            cache_key = 'product_cache'
            data = cache.get(cache_key)
            if not data:
                serializer = self.get_serializer(self.get_queryset(), many=True)
                data = serializer.data
                cache.set(cache_key, data, 600)
            return Response(data, status=200)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('product_cache')
        transaction.on_commit(lambda: update_product_cache.delay())


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category', 'shop').prefetch_related(
        'product_images', 'product_reviews__user'
    ).annotate(avg_rating_val=Avg('product_reviews__mark')).all()
    serializer_class = ProductSerializer
    permission_classes = [IsProductShopOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save()
        cache.delete('product_cache')
        transaction.on_commit(lambda: update_product_cache.delay())

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('product_cache')
        transaction.on_commit(lambda: update_product_cache.delay())


class ProductImageListCreateView(generics.ListCreateAPIView):
    queryset = ProductImage.objects.select_related(
        'product', 'product__shop', 'product__shop__user'
    ).all().order_by('-created_at')
    serializer_class = ProductImageSerializer
    permission_classes = [IsImageShopOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.select_related(
        'product', 'product__shop', 'product__shop__user'
    ).all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsImageShopOwnerOrReadOnly]


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related('user', 'product').all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]


class RecommendationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        base_qs = Product.objects.select_related('category', 'shop').prefetch_related(
            'product_images', 'product_reviews__user'
        ).annotate(avg_rating_val=Avg('product_reviews__mark'))
        recommended = []
        seen_ids = set()

        if request.user.is_authenticated:
            queries = SearchHistory.objects.filter(user=request.user).order_by('-created_at').values_list('query', flat=True)
            for query in queries:
                matches = base_qs.filter(
                    Q(title__icontains=query) | Q(description__icontains=query)
                )[:5]
                for product in matches:
                    if product.id not in seen_ids:
                        seen_ids.add(product.id)
                        recommended.append(product)

        if not recommended:
            recommended = list(base_qs.order_by('-created_at')[:10])

        serializer = ProductSerializer(recommended, many=True)
        return Response(serializer.data, status=200)


class StatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories_products = Category.objects.annotate(
            products_count=Count('category_products', distinct=True)
        ).values('id', 'name', 'products_count')

        shops_products = Shop.objects.annotate(
            products_count=Count('shop_products', distinct=True),
            rating=Avg('shop_products__product_reviews__mark')
        ).values('id', 'name', 'products_count', 'rating')

        top_products = Product.objects.annotate(
            orders_count=Count('product_order_items', distinct=True)
        ).order_by('-orders_count')[:5].values('id', 'title', 'orders_count')

        top_rated_products = Product.objects.annotate(
            avg_rating=Avg('product_reviews__mark'),
            reviews_count=Count('product_reviews', distinct=True)
        ).filter(reviews_count__gt=0).order_by('-avg_rating', '-reviews_count')[:5].values(
            'id', 'title', 'avg_rating', 'reviews_count'
        )

        most_wished_products = Product.objects.annotate(
            wishes_count=Count('product_wishes', distinct=True)
        ).order_by('-wishes_count')[:5].values('id', 'title', 'wishes_count')

        stats = {
            'total_users': CustomUser.objects.aggregate(total=Count('id'))['total'],
            'total_shops': Shop.objects.aggregate(total=Count('id'))['total'],
            'total_categories': Category.objects.aggregate(total=Count('id'))['total'],
            'total_products': Product.objects.aggregate(total=Count('id'))['total'],
            'total_orders': Order.objects.aggregate(total=Count('id'))['total'],
            'total_reviews': Review.objects.aggregate(total=Count('id'))['total'],
        }

        return Response({
            'stats': stats,
            'categories_products_count': list(categories_products),
            'shops_products_count': list(shops_products),
            'top_products': list(top_products),
            'top_rated_products': list(top_rated_products),
            'most_wished_products': list(most_wished_products),
        })
