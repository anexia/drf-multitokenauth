""" URL Configuration for core auth
"""
from django.conf.urls import url, include
from django_rest_multitokenauth.views import login_and_obtain_auth_token, logout_and_delete_auth_token

app_name = 'django_rest_multitokenauth'

urlpatterns = [
    url(r'^login', login_and_obtain_auth_token, name="auth-login"),  # normal login with session
    url(r'^logout', logout_and_delete_auth_token, name="auth-logout")
]
