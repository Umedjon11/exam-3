from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    ProductImageListCreateView,
    ProductImageDetailView,
    ReviewListCreateView,
    ReviewDetailView,
    RecommendationView,
    StatsView,
)


urlpatterns = [
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('recommendations/', RecommendationView.as_view()),
    path('stats/', StatsView.as_view()),
    path('product-images/', ProductImageListCreateView.as_view()),
    path('product-images/<int:pk>/', ProductImageDetailView.as_view()),
    path('reviews/', ReviewListCreateView.as_view()),
    path('reviews/<int:pk>/', ReviewDetailView.as_view()),
]
