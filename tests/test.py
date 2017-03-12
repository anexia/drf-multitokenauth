import json
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.test import APITestCase
from django_rest_multitokenauth.models import MultiToken


# try getting reverse from django.urls
try:
    # Django 1.10 +
    from django.urls import reverse
except:
    # Django 1.8 and 1.9
    from django.core.urlresolvers import reverse


class HelperMixin:
    """
    Mixin which encapsulates methods for login, logout, request reset password and reset password confirm
    """
    def setUpUrls(self):
        self.login_url = reverse('multi_token_auth:auth-login')
        self.logout_url = reverse('multi_token_auth:auth-logout')
        self.reset_password_request_url = reverse('multi_token_auth:auth-reset-password-request')
        self.reset_passwordconfirm_url = reverse('multi_token_auth:auth-reset-password-confirm')

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


class AuthTestCase(APITestCase, HelperMixin):
    def setUp(self):
        self.setUpUrls()
        self.user1 = User.objects.create_user("user1", "user1@mail.com", "secret1")
        self.user2 = User.objects.create_user("user2", "user2@mail.com", "secret2")

    def login_and_obtain_token(self, username, password,  HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        response = self.rest_do_login(username, password, HTTP_USER_AGENT, REMOTE_ADDR)
        self.assertContains(response, "{\"token\":\"")

        content = json.loads(response.content.decode())
        token = content['token']

        return token

    def test_login_and_logout(self):
        """ tests login and logout """
        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

        token = self.login_and_obtain_token('user1', 'secret1')
        self.assertEqual(MultiToken.objects.all().count(), 1)
        # verify the token is for user 1
        self.assertEqual(
            MultiToken.objects.filter(key=token).first().user.username,
            'user1'
        )

        # logout
        response = self.rest_do_logout(token)
        # make sure the response is "logged_out"
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "{\"status\":\"logged out\"}")

        # there should now again be zero tokens in the database
        self.assertEqual(MultiToken.objects.all().count(), 0)

    def test_login_multiple_times(self):
        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

        # login first time
        token1 = self.login_and_obtain_token('user1', 'secret1')
        self.assertEqual(MultiToken.objects.all().count(), 1)
        # verify the token is for user 1
        self.assertEqual(
            MultiToken.objects.filter(key=token1).first().user.username,
            'user1'
        )

        # login second time
        token2 = self.login_and_obtain_token('user1', 'secret1')
        self.assertEqual(MultiToken.objects.all().count(), 2)
        # verify the token is for user 1
        self.assertEqual(
            MultiToken.objects.filter(key=token2).first().user.username,
            'user1'
        )
        # verify that token1 is not equal to token2
        self.assertNotEqual(token1, token2)

        # login third time
        token3 = self.login_and_obtain_token('user1', 'secret1')
        self.assertEqual(MultiToken.objects.all().count(), 3)
        # verify the token is for user 1
        self.assertEqual(
            MultiToken.objects.filter(key=token3).first().user.username,
            'user1'
        )
        # verify that token is not equal to token2 and token3
        self.assertNotEqual(token1, token3)
        self.assertNotEqual(token2, token3)

        # Now logout with token2 and verify that token1 and token3 are still in database
        response = self.rest_do_logout(token2)
        self.assertEqual(response.status_code, 200)
        # should be two tokens left
        self.assertEqual(MultiToken.objects.all().count(), 2)
        # verify that these two are token1 and token3
        self.assertEqual(
            MultiToken.objects.filter(Q(key=token1) | Q(key=token3)).count(),
            2
        )

    def test_login_with_invalid_credentials(self):
        # correct username, but wrong password
        response = self.rest_do_login("user1", "wrongpassword")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertTrue('non_field_errors' in content)

        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

        # wrong username, but correct password
        response = self.rest_do_login("userOne", "secret1")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertTrue('non_field_errors' in content)

        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

        # wrong username, wrong password
        response = self.rest_do_login("userOne", "wrongpassword")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertTrue('non_field_errors' in content)

        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)


    def test_login_multiple_users(self):
        pass

    def test_reset_password(self):
        pass

    def test_reset_password_multiple_users(self):
        pass

    def test_reset_password_multiple_users(self):
        pass