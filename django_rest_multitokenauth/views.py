from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header

from django_rest_multitokenauth.models import MultiToken


class LogoutAndDeleteAuthToken(APIView):
    """ Custom API View for logging out"""

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            # delete this users auth token
            auth_header = get_authorization_header(request)

            token = auth_header.split()[1].decode()
            tokens = MultiToken.objects.filter(key=token, user=request.user)
            if len(tokens) == 1:
                tokens.delete()
                return Response({'status': 'logged out'})
            else:
                return Response({'error': 'invalid token'})

        return Response({'error': 'not logged in'})


class LoginAndObtainAuthToken(APIView):
    """ Custom View for logging in and getting the auth token """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.is_authenticated():
            token = MultiToken.objects.create(
                user=user,
                user_agent=request.META['HTTP_USER_AGENT'],
                last_known_ip=request.META['REMOTE_ADDR']
            )
            return Response({'token': token.key})
        # else:
        return Response({'error': 'not logged in'})


login_and_obtain_auth_token = LoginAndObtainAuthToken.as_view()
logout_and_delete_auth_token = LogoutAndDeleteAuthToken.as_view()
