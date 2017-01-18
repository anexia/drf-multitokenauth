""" contains basic admin views for MultiToken """
from django.contrib import admin
from django_rest_multitokenauth.models import MultiToken, ResetPasswordToken


@admin.register(MultiToken)
class MultiTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'user_agent')


@admin.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'ip_address', 'user_agent')