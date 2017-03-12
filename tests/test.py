import json
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django_rest_multitokenauth.models import MultiToken

class GenericTestCase(TestCase):
    def test_generic(self):
        self.assertEquals(True, True)


class LoginLogoutHelperMixin:
    def set_client_credentials(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def reset_client_credentials(self):
        self.client.credentials()

    def rest_do_login(self, username, password, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        data = {
            'username': username,
            'password': password
        }
        return self.client.post(
            self.login_url,
            data,
            format='json',
            HTTP_USER_AGENT=HTTP_USER_AGENT,
            REMOTE_ADDR=REMOTE_ADDR
        )

    def rest_do_logout(self, token, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        self.set_client_credentials(token)

        # call logout
        return self.client.post(
            self.logout_url,
            format='json',
            HTTP_USER_AGENT=HTTP_USER_AGENT,
            REMOTE_ADDR=REMOTE_ADDR
        )



class LoginLogoutTestCase(APITestCase, LoginLogoutHelperMixin):
    def setUp(self):
        self.user1 = User.objects.create_user("user1", "user1@mail.com", "secret1")
        self.user2 = User.objects.create_user("user2", "user2@mail.com", "secret2")
        self.login_url = reverse('multi_token_auth:auth-login')
        self.logout_url = reverse('multi_token_auth:auth-logout')

    def login_and_obtain_token(self, username, password,  HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        response = self.rest_do_login(username, password, HTTP_USER_AGENT, REMOTE_ADDR)
        self.assertContains(response, "{\"token\":\"")

        content = json.loads(response.content.decode())
        token = content['token']

        return token


    def test_login(self):
        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

        token = self.login_and_obtain_token('user1', 'secret1')
        self.assertEqual(MultiToken.objects.all().count(), 1)

        # logout
        response = self.rest_do_logout(token)
        # make sure the response is "logged_out"
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "{\"status\":\"logged out\"}")
