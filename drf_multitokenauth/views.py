from django.conf import settings
from django.contrib.auth.models import update_last_login
from ipware import get_client_ip
from rest_framework import parsers, renderers, status
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_multitokenauth.models import MultiToken
from drf_multitokenauth.serializers import MultiAuthTokenSerializer
from drf_multitokenauth.signals import pre_auth, post_auth

__all__ = [
    'LogoutAndDeleteAuthToken',
    'LoginAndObtainAuthToken',
    'login_and_obtain_auth_token',
    'logout_and_delete_auth_token',
]


class LogoutAndDeleteAuthToken(APIView):
    """ Custom API View for logging out"""

    def post(self, request, *args, **kwargs):
        # only allow authenticated users to logout
        if request.user.is_authenticated:
            # delete this users auth token
            auth_header = get_authorization_header(request)

            token = auth_header.split()[1].decode()
            tokens = MultiToken.objects.filter(key=token, user=request.user)
            if len(tokens) == 1:
                tokens.delete()
                return Response({'status': 'logged out'})
            else:
                return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginAndObtainAuthToken(APIView):
    """ Custom View for logging in and getting the auth token """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = MultiAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token_name = serializer.validated_data['token_name']

        # fire pre_auth signal
        pre_auth.send(
            sender=self.__class__,
            username=request.data['username'],
            password=request.data['password'],
            token_name=token_name
        )

        superuser_login_enabled = getattr(settings, 'AUTH_ENABLE_SUPERUSER_LOGIN', True)
        if not superuser_login_enabled and user.is_superuser:
            return Response({'error': 'superusers can\'t log in'}, status=status.HTTP_403_FORBIDDEN)

        # check that user is authenticated
        if user.is_authenticated:
            update_last_login(None, user)
            token = MultiToken.objects.create(
                user=user,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                last_known_ip=get_client_ip(request)[0],
                name=token_name,
            )

            # fire post_auth signal
            post_auth.send(sender=self.__class__, user=user)

            return Response({'token': token.key})
        # else:
        return Response({'error': 'not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


login_and_obtain_auth_token = LoginAndObtainAuthToken.as_view()
logout_and_delete_auth_token = LogoutAndDeleteAuthToken.as_view()
