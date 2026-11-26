from django.urls import path
from .views import (
    ProfileUpdateView,
    ProfileDetailView,
    DeliveryAddressListCreateView,
    DeliveryAddressDetailView,
    SearchHistoryListView,
    SearchHistoryDetailView,
)

profile_urlpatterns = [
    path('update/', ProfileUpdateView.as_view()),
    path('<int:pk>/', ProfileDetailView.as_view()),
]

address_urlpatterns = [
    path('', DeliveryAddressListCreateView.as_view()),
    path('<int:pk>/', DeliveryAddressDetailView.as_view()),
]

search_history_urlpatterns = [
    path('', SearchHistoryListView.as_view()),
    path('<int:pk>/', SearchHistoryDetailView.as_view()),
]
