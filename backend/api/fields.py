import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
    """Кодирует картинку в строку base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            forma1t, imgstr = data.split(";base64,")
            ext = forma1t.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)
