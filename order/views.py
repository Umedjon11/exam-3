from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from account.permissions import IsOwner
from product.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .tasks import process_order


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).select_related(
            'user', 'address'
        ).prefetch_related('order_items__product').order_by('-created_at')

    def perform_create(self, serializer):
        order = serializer.save()
        transaction.on_commit(lambda: process_order.delay(order.id))


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).select_related(
            'user', 'address'
        ).prefetch_related('order_items__product')


class OrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return OrderItem.objects.none()
        queryset = OrderItem.objects.filter(order__user=self.request.user).select_related(
            'product', 'order', 'order__user'
        ).order_by('-created_at')
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset


class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related('order_items__product'),
            id=pk,
            user=request.user
        )

        if order.status == 'cancelled':
            return Response(
                {"detail": "Order is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == 'completed':
            return Response(
                {"detail": "Completed order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            for item in order.order_items.all():
                product = Product.objects.select_for_update().get(id=item.product_id)
                product.stock += item.quantity
                product.save()

            order.status = 'cancelled'
            order.save()

        cache.delete('product_cache')
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
