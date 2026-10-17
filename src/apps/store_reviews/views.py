from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from api.pagination import CustomPagination

from .models import StoreReview
from .serializers import StoreReviewCreateSerializer, StoreReviewSerializer
from .throttles import StoreReviewCreateThrottle


class StoreReviewPagination(CustomPagination):
    """{count, pages, results}; maketda bir sahifada 8 ta sharh"""

    page_size = 8
    max_page_size = 50


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class StoreReviewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Do'kon haqidagi sharhlar ("Отзывы" sahifasi).

    GET  /store-reviews/?ordering=-created_at&page=2  — faqat tasdiqlanganlar
    POST /store-reviews/  (multipart: name, email, text, images[])
         — login shart emas; admin tasdiqlaguncha ko'rinmaydi.
    """

    # Login talab qilinmaydi: eskirgan token yoki session CSRF xato bermasligi uchun
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    pagination_class = StoreReviewPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at", "-id"]

    def get_queryset(self):
        return StoreReview.objects.filter(is_approved=True).prefetch_related("images")

    def get_serializer_class(self):
        if self.action == "create":
            return StoreReviewCreateSerializer
        return StoreReviewSerializer

    def get_throttles(self):
        if self.action == "create":
            return [StoreReviewCreateThrottle()]
        return []

    @extend_schema(
        request={"multipart/form-data": StoreReviewCreateSerializer},
        responses={201: StoreReviewSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(ip_address=client_ip(request))

        output = StoreReviewSerializer(review, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)
