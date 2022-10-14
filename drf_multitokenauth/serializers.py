from rest_framework import serializers

__all__ = [
    'EmailSerializer',
]


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
