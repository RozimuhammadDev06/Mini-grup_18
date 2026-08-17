

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

