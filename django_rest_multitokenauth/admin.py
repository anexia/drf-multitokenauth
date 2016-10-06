""" contains basic admin views for MultiToken """
from django.contrib import admin
from django_rest_multitokenauth.models import MultiToken


@admin.register(MultiToken)
class MultiTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'user_agent')
