""" URL Configuration for core auth
"""
from django.urls import re_path

from drf_multitokenauth.views import login_and_obtain_auth_token, logout_and_delete_auth_token

app_name = 'drf_multitokenauth'

urlpatterns = [
    re_path(r'^login', login_and_obtain_auth_token, name="auth-login"),  # normal login with session
    re_path(r'^logout', logout_and_delete_auth_token, name="auth-logout")
]
