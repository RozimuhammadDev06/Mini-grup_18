from rest_framework import serializers

from . import limits
from .models import StoreReview, StoreReviewImage


def absolute_url(request, file_field):
    if not file_field:
        return None
    return request.build_absolute_uri(file_field.url) if request else file_field.url


class StoreReviewSerializer(serializers.ModelSerializer):
    """Saytda ko'rsatiladigan sharh (email va IP yo'q)"""

    images = serializers.SerializerMethodField()

    class Meta:
        model = StoreReview
        fields = ["id", "name", "text", "images", "is_approved", "created_at"]
        read_only_fields = fields

    def get_images(self, obj) -> list[str]:
        request = self.context.get("request")
        return [absolute_url(request, item.image) for item in obj.images.all()]


class StoreReviewCreateSerializer(serializers.ModelSerializer):
    """
    Yangi sharh: multipart/form-data
      name, email, text, images (bir nechta fayl — bir xil "images" kaliti bilan)
    """

    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
        max_length=limits.MAX_IMAGES,
        error_messages={"max_length": f"Можно прикрепить не более {limits.MAX_IMAGES} фото."},
    )

    class Meta:
        model = StoreReview
        fields = ["name", "email", "text", "images"]
        extra_kwargs = {
            "name": {"error_messages": {"blank": "Укажите ваше имя."}},
            "email": {"error_messages": {"blank": "Укажите email.", "invalid": "Некорректный email."}},
            "text": {"error_messages": {"blank": "Напишите текст отзыва."}},
        }

    def validate_name(self, value):
        value = value.strip()
        if len(value) < limits.NAME_MIN_LENGTH:
            raise serializers.ValidationError("Укажите ваше имя.")
        return value

    def validate_text(self, value):
        value = value.strip()
        if len(value) < limits.TEXT_MIN_LENGTH:
            raise serializers.ValidationError(
                f"Минимум {limits.TEXT_MIN_LENGTH} символов."
            )
        return value

    def validate_images(self, files):
        max_bytes = limits.MAX_IMAGE_SIZE_MB * 1024 * 1024
        for file in files:
            if file.size > max_bytes:
                raise serializers.ValidationError(
                    f"Файл «{file.name}» больше {limits.MAX_IMAGE_SIZE_MB} МБ."
                )
            # ImageField faylni Pillow bilan ochib tekshirgan — haqiqiy formatini olamiz
            image_format = getattr(getattr(file, "image", None), "format", None)
            if image_format not in limits.ALLOWED_IMAGE_FORMATS:
                raise serializers.ValidationError(
                    f"Файл «{file.name}»: допустимы только JPG, PNG и WEBP."
                )
        return files

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        review = StoreReview.objects.create(**validated_data)
        StoreReviewImage.objects.bulk_create(
            [StoreReviewImage(review=review, image=file, sort=index) for index, file in enumerate(images)]
        )
        return review
