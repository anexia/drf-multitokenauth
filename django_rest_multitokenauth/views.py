from django.contrib.auth.models import User
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header
from django.core.exceptions import ValidationError

from django_rest_multitokenauth.models import MultiToken
from django_rest_multitokenauth.serializers import EmailSerializer, PasswordTokenSerializer
from django_rest_multitokenauth.models import ResetPasswordToken
from django_rest_multitokenauth.signals import reset_password_token_created

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


class ResetPasswordConfirm(APIView):
    """
    An Api View which provides a method to reset a password based on a unique token
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = PasswordTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        token = serializer.validated_data['token']

        # find token
        reset_password_token = ResetPasswordToken.objects.get(key=token)

        # change users password
        if reset_password_token.user.has_usable_password():
            reset_password_token.user.set_password(password)
            reset_password_token.user.save()

        # delete token
        reset_password_token.delete()

        return Response({'status': 'OK'})


class ResetPasswordRequestToken(APIView):
    """
    An Api View which provides a method to request a password reset token based on an e-mail address

    Sends a signal reset_password_token_created when a reset token was created
    """
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = EmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # find a user by email address
        users = User.objects.filter(email=email)

        active_user_found = False

        for user in users:
            if user.is_active and user.has_usable_password():
                active_user_found = True

        if not active_user_found:
            raise ValidationError({
                'email': ValidationError(
                    _("There is no active user associated with this e-mail address or the password can not be changed"),
                    code='invalid')}
            )

        for user in users:
            if user.is_active and user.has_usable_password():
                token = ResetPasswordToken.objects.create(
                    user=user,
                    user_agent=request.META['HTTP_USER_AGENT'],
                    ip_address=request.META['REMOTE_ADDR']
                )
                # send a signal that the password token was created
                # let whoever receives this signal handle sending the email for the password reset
                reset_password_token_created.send(sender=self.__class__, reset_password_token=token)
        return Response({'status': 'OK'})


login_and_obtain_auth_token = LoginAndObtainAuthToken.as_view()
logout_and_delete_auth_token = LogoutAndDeleteAuthToken.as_view()
reset_password_confirm = ResetPasswordConfirm.as_view()
reset_password_request_token = ResetPasswordRequestToken.as_view()
