from django.db import models
from django.conf import settings

class Article(models.Model):
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    image = models.ImageField(upload_to='articles/')
    published_at = models.DateTimeField()

from django.db import models

class Promotion(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True) # yoki ImageField
    discount_label = models.CharField(max_length=100, blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    category = models.ForeignKey('catalog.Category', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
    
class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    link = models.CharField(max_length=255)
    sort = models.IntegerField(default=0)

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    sort = models.IntegerField(default=0)

class StaticPage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    body = models.TextField()

class Review(models.Model):
    """
    Note: Reviews are for the store, not specific products.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)

class Compare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    category = models.ForeignKey('catalog.Category', on_delete=models.CASCADE)

class Lead(models.Model):
    type = models.CharField(max_length=50) # e.g., 'callback', 'question'
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    product_id = models.IntegerField(null=True, blank=True)
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='new')
