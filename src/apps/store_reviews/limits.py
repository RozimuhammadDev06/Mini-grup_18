"""
Sharh cheklovlari — frontenddagi forma bilan bir xil
(mini-18: components/reviews/ReviewForm.tsx, data/reviewsData.ts -> REVIEW_PHOTO_LIMITS).
"""

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 100

TEXT_MIN_LENGTH = 10
TEXT_MAX_LENGTH = 3000

MAX_IMAGES = 5
MAX_IMAGE_SIZE_MB = 5
# Pillow formati nomlari (fayl kengaytmasiga emas, haqiqiy mazmuniga qaraladi)
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

# Bitta IP'dan yangi sharhlar soni
CREATE_RATE = "3/hour"
