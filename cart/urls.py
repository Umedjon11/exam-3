from django.urls import path
from .views import (
    CartView,
    CartClearView,
    CartItemListCreateView,
    CartItemDetailView,
    WishListCreateView,
    WishDetailView,
)


urlpatterns = [
    path('cart/', CartView.as_view()),
    path('cart/clear/', CartClearView.as_view()),
    path('cart/items/', CartItemListCreateView.as_view()),
    path('cart/items/<int:pk>/', CartItemDetailView.as_view()),
    path('wishes/', WishListCreateView.as_view()),
    path('wishes/<int:pk>/', WishDetailView.as_view()),
]
