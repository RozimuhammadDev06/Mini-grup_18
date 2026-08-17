

from rest_framework import viewsets, permissions
from .models import Review, Wishlist, Compare, Lead
from .serializers import ReviewSerializer, WishlistSerializer, CompareSerializer, LeadSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_published=True)
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CompareViewSet(viewsets.ModelViewSet):
    serializer_class = CompareSerializer

    def get_queryset(self):
        user = self.request.user
        session_key = self.request.headers.get('X-Session-Key')
        if user.is_authenticated:
            return Compare.objects.filter(user=user)
        elif session_key:
            return Compare.objects.filter(session_key=session_key)
        return Compare.objects.none()

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.AllowAny]



from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Wishlist
from .serializers import WishlistSerializer

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only see their own favorite products
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Custom action to add/remove a product from wishlist with one click.
        POST /api/engagement/wishlist/toggle/ { "product_id": 123 }
        """
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()

        if wishlist_item:
            # If it exists, remove it (Unlike)
            wishlist_item.delete()
            return Response({"status": "removed", "message": "Product removed from wishlist"}, status=status.HTTP_200_OK)
        else:
            # If it doesn't exist, create it (Like)
            Wishlist.objects.create(user=request.user, product_id=product_id)
            return Response({"status": "added", "message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)
