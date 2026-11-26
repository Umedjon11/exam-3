from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view


from account.extra_urls import (
    profile_urlpatterns,
    address_urlpatterns,
    search_history_urlpatterns,
)


schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    path('admin/', admin.site.urls),
    path('auth/', include('account.urls')),
    path('profile/', include(profile_urlpatterns)),
    path('addresses/', include(address_urlpatterns)),
    path('search-history/', include(search_history_urlpatterns)),
    path('shops/', include('shop.urls')),
    path('', include('product.urls')),
    path('', include('cart.urls')),
    path('orders/', include('order.urls')),
]
