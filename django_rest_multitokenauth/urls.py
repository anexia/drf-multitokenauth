""" URL Configuration for core auth
"""
from django.conf.urls import url, include
from django_rest_multitokenauth.views import login_and_obtain_auth_token, logout_and_delete_auth_token, reset_password_request_token, reset_password_confirm

urlpatterns = [
    url(r'^login', login_and_obtain_auth_token, name="auth-login"),  # normal login with session
    url(r'^logout', logout_and_delete_auth_token, name="auth-logout"),
    url(r'^reset_password/confirm', reset_password_confirm, name="auth-reset-password-confirm"),
    url(r'^reset_password', reset_password_request_token, name="auth-reset-password-request"),
]
