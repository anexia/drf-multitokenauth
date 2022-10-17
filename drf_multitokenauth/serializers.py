from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

__all__ = [
    'EmailSerializer',
]


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class MultiAuthTokenSerializer(AuthTokenSerializer):
    token_name = serializers.CharField(required=False, default="", allow_blank=True)
