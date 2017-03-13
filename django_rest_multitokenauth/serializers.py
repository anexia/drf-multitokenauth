from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
