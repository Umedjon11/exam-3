from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderItemListView,
    OrderCancelView,
)


urlpatterns = [
    path('', OrderListCreateView.as_view()),
    path('<int:pk>/', OrderDetailView.as_view()),
    path('<int:pk>/cancel/', OrderCancelView.as_view()),
    path('items/', OrderItemListView.as_view()),
]
