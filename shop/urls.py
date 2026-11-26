from django.urls import path
from .views import ShopListCreateView, ShopDetailView, MyShopView


urlpatterns = [
    path('', ShopListCreateView.as_view()),
    path('my-shop/', MyShopView.as_view()),
    path('<int:pk>/', ShopDetailView.as_view()),
]
