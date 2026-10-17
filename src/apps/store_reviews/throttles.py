from rest_framework.throttling import SimpleRateThrottle

from . import limits


class StoreReviewCreateThrottle(SimpleRateThrottle):
    """
    Bitta IP'dan yangi sharhlar soni cheklangan (spamdan himoya).
    Rate shu yerda beriladi — settings'dagi DEFAULT_THROTTLE_RATES ga bog'liq emas.
    """

    scope = "store_review_create"
    rate = limits.CREATE_RATE

    def get_rate(self):
        return self.rate

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}
