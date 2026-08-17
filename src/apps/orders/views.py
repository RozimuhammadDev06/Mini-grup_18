from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Cart, CartItem, Order
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.headers.get("X-Session-Key")

        if user.is_authenticated:
            return Cart.objects.filter(user=user)

        elif session_key:
            return Cart.objects.filter(session_key=session_key)

        return Cart.objects.none()

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        cart = self.get_object()

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {"error": "quantity must be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.catalog.models import Product

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        item.price = product.price
        item.save()

        serializer = CartSerializer(cart)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            number=f"SO-{1000 + Order.objects.count()}"
        )





from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from apps.orders.models import Cart # Import Cart to move items to Order

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view their own order history
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'items__product')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Creates the Order, copies Cart items to OrderItems (with snapshots),
        and clears the Cart.
        """
        user = self.request.user
        
        # 1. Generate a unique order number
        order_number = f"SO-{Order.objects.filter(user=user).count() + 1000}"

        # 2. Save the main Order
        order = serializer.save(user=user, number=order_number)

        # 3. Find the user's current cart
        cart = Cart.objects.filter(user=user).first()
        if not cart:
            # If no cart, return an empty order (or raise error based on business logic)
            pass
        else:
            # 4. Move items from Cart to OrderItem with snapshots
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    name_snapshot=cart_item.product.name,
                    article_snapshot=cart_item.product.article,
                    price=cart_item.price,
                    quantity=cart_item.quantity
                )
            # 5. Clear the cart
            cart.items.all().delete()
