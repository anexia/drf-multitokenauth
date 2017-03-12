""" Tests App URL Config """
from django.conf.urls import url, include

urlpatterns = [
    url(r'^api/auth/', include('django_rest_multitokenauth.urls', namespace='multi_token_auth')),
]
