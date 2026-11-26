from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from account.permissions import IsOwner
from .models import Cart, CartItem, Wish
from .permissions import IsCartItemOwner
from .serializers import CartSerializer, CartItemSerializer, WishSerializer


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.select_related('user').prefetch_related(
            'cart_items__product__category', 'cart_items__product__shop'
        ).get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.cart_items.all().delete()
        return Response({"detail": "Cart cleared"}, status=status.HTTP_200_OK)


class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related(
            'cart', 'product', 'product__category', 'product__shop'
        ).order_by('-created_at')


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsCartItemOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        return CartItem.objects.filter(cart__user=self.request.user).select_related(
            'cart', 'cart__user', 'product', 'product__category', 'product__shop'
        )


class WishListCreateView(generics.ListCreateAPIView):
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Wish.objects.none()
        return Wish.objects.filter(user=self.request.user).select_related(
            'user', 'product', 'product__category', 'product__shop'
        ).order_by('-created_at')


class WishDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WishSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Wish.objects.none()
        return Wish.objects.filter(user=self.request.user).select_related(
            'user', 'product', 'product__category', 'product__shop'
        )
