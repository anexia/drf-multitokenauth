""" Tests App URL Config """
from django.conf.urls import include
from django.urls import re_path

urlpatterns = [
    re_path(r'^api/auth/', include('drf_multitokenauth.urls', namespace='multi_token_auth')),
]
