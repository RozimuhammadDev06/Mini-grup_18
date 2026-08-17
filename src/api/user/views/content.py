from rest_framework import viewsets
from apps.content.models import Article, Promotion, Banner, FAQ, StaticPage
from api.user.serializers.content_serializers import ArticleSerializer, PromotionSerializer, BannerSerializer, FAQSerializer, StaticPageSerializer

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.all().order_by('sort')
    serializer_class = BannerSerializer

class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.all().order_by('sort')
    serializer_class = FAQSerializer

class StaticPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'
