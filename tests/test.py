import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from drf_multitokenauth.models import MultiToken


class HelperMixin:
    """
    Mixin which encapsulates methods for login and logout
    """
    def setUpUrls(self):
        """ set up urls by using djangos reverse function """
        self.login_url = reverse('multi_token_auth:auth-login')
        self.logout_url = reverse('multi_token_auth:auth-logout')

    def set_client_credentials(self, token):
        """ set client credentials, namely the auth token """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def reset_client_credentials(self):
        """ reset all client credentials """
        self.client.credentials()

    def rest_do_login(self, username, password, token_name=None, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        """ REST API Wrapper for login """
        data = {
            'username': username,
            'password': password
        }

        if token_name is not None:
            data['token_name'] = token_name

        return self.client.post(
            self.login_url,
            data,
            format='json',
            HTTP_USER_AGENT=HTTP_USER_AGENT,
            REMOTE_ADDR=REMOTE_ADDR
        )

    def rest_do_logout(self, token, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        """ REST API wrapper for logout """
        if token:
            self.set_client_credentials(token)

        # call logout
        return self.client.post(
            self.logout_url,
            format='json',
            HTTP_USER_AGENT=HTTP_USER_AGENT,
            REMOTE_ADDR=REMOTE_ADDR
        )


class AuthTestCase(APITestCase, HelperMixin):
    """
    Several Test Cases for the Multi Auth Token Django App
    """
    def setUp(self):
        self.setUpUrls()
        self.user1 = User.objects.create_user("user1", "user1@mail.com", "secret1")
        self.user2 = User.objects.create_user("user2", "user2@mail.com", "secret2")
        self.superuser = User.objects.create_superuser("superuser", "superuser@mail.com", "secret3")

    def login_and_obtain_token(self, username, password, token_name=None, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        response = self.rest_do_login(username, password, token_name, HTTP_USER_AGENT, REMOTE_ADDR)
        self.assertContains(response, "{\"token\":\"")

        content = json.loads(response.content.decode())
        token = content['token']

        return token

    def test_login_and_logout(self):
        """ tests login and logout for a single user """
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
        """ tests login with the same user for several times """
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should be two tokens left
        self.assertEqual(MultiToken.objects.all().count(), 2)
        # verify that these two are token1 and token3
        self.assertEqual(
            MultiToken.objects.filter(Q(key=token1) | Q(key=token3)).count(),
            2
        )

    def test_login_with_token_name(self):
        """ tests login several times, using the same or different token_names for one or more users """
        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

        # login first time without token_name (defaults to '')
        token1 = self.login_and_obtain_token('user1', 'secret1')
        self.assertEqual(MultiToken.objects.all().count(), 1)
        # verify the token is for user 1 and has an empty token_name
        multi_token1 = MultiToken.objects.filter(key=token1).first()
        self.assertEqual(
            multi_token1.user.username,
            'user1'
        )
        self.assertEqual(multi_token1.name, '')

        # login second time with empty token_name ''
        token2 = self.login_and_obtain_token('user1', 'secret1', '')
        self.assertEqual(MultiToken.objects.all().count(), 2)
        # verify the token is for user 1 and has an empty token_name
        multi_token2 = MultiToken.objects.filter(key=token2).first()
        self.assertEqual(
            multi_token2.user.username,
            'user1'
        )
        self.assertEqual(multi_token2.name, '')
        # verify that token1 is not equal to token2
        self.assertNotEqual(token1, token2)

        # login third time, with token_name
        token3 = self.login_and_obtain_token('user1', 'secret1', 'test_token_name1')
        self.assertEqual(MultiToken.objects.all().count(), 3)
        # verify the token is for user 1 and has an empty token_name
        multi_token3 = MultiToken.objects.filter(key=token3).first()
        self.assertEqual(
            multi_token3.user.username,
            'user1'
        )
        self.assertEqual(multi_token3.name, 'test_token_name1')
        # verify that token2 is not equal to token3
        self.assertNotEqual(token2, token3)

        # login third time, with same token_name
        token4 = self.login_and_obtain_token('user1', 'secret1', 'test_token_name1')
        self.assertEqual(MultiToken.objects.all().count(), 4)
        # verify the token is for user 1 and has an empty token_name
        multi_token4 = MultiToken.objects.filter(key=token4).first()
        self.assertEqual(
            multi_token4.user.username,
            'user1'
        )
        self.assertEqual(multi_token4.name, 'test_token_name1')
        # verify that token3 is not equal to token4
        self.assertNotEqual(token3, token4)

        # login with another user and the same token_name
        token5 = self.login_and_obtain_token('user2', 'secret2', 'test_token_name1')
        self.assertEqual(MultiToken.objects.all().count(), 5)
        # verify the token is for user 1 and has an empty token_name
        multi_token5 = MultiToken.objects.filter(key=token5).first()
        self.assertEqual(
            multi_token5.user.username,
            'user2'
        )
        self.assertEqual(multi_token5.name, 'test_token_name1')
        # verify that token4 is not equal to token5
        self.assertNotEqual(token4, token5)

        # login with same user and different token_name
        token6 = self.login_and_obtain_token('user2', 'secret2', 'test_token_name2')
        self.assertEqual(MultiToken.objects.all().count(), 6)
        # verify the token is for user 1 and has an empty token_name
        multi_token6 = MultiToken.objects.filter(key=token6).first()
        self.assertEqual(
            multi_token6.user.username,
            'user2'
        )
        self.assertEqual(multi_token6.name, 'test_token_name2')
        # verify that token5 is not equal to token6
        self.assertNotEqual(token5, token6)

    def test_login_with_invalid_credentials(self):
        """ tests login with invalid credentials """
        # log in one time, just to be sure that the login works
        self.login_and_obtain_token("user1", "secret1")
        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

        # correct username, but wrong password
        response = self.rest_do_login("user1", "wrongpassword")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in content)

        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

        # wrong username, but correct password
        response = self.rest_do_login("userOne", "secret1")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in content)

        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

        # wrong username, wrong password
        response = self.rest_do_login("userOne", "wrongpassword")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('non_field_errors' in content)
        self.assertFalse('token' in content, msg="There should not be a token in the response")

        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

    def test_login_multiple_users(self):
        """ Login with multiple accounts and obtain several tokens """
        token1 = self.login_and_obtain_token("user1", "secret1")
        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)
        # check that token1 is assigned to user1
        self.assertEqual(MultiToken.objects.filter(key=token1).first().user.username, "user1")

        token2 = self.login_and_obtain_token("user2", "secret2")
        # there should be two tokens
        self.assertEqual(MultiToken.objects.all().count(), 2)
        # check that token1 is assigned to user1
        self.assertEqual(MultiToken.objects.filter(key=token1).first().user.username, "user1")
        # check that token2 is assigned to user2
        self.assertEqual(MultiToken.objects.filter(key=token2).first().user.username, "user2")

        # login again with user1
        token3 = self.login_and_obtain_token("user1", "secret1")
        # there should be three tokens
        self.assertEqual(MultiToken.objects.all().count(), 3)
        # check that token1 is assigned to user1
        self.assertEqual(MultiToken.objects.filter(key=token1).first().user.username, "user1")
        # check that token2 is assigned to user2
        self.assertEqual(MultiToken.objects.filter(key=token2).first().user.username, "user2")
        # check that token3 is assigned to user1
        self.assertEqual(MultiToken.objects.filter(key=token3).first().user.username, "user1")

    def test_login_with_superuser_enabled(self):
        """ tests login with superuser when the setting is enabled (by default) """
        # log in one time, just to be sure that the login works
        self.login_and_obtain_token("superuser", "secret3")
        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

    @override_settings(AUTH_ENABLE_SUPERUSER_LOGIN=False)
    def test_login_with_superuser_disabled(self):
        """ tests login with superuser when the setting is disabled """
        # logging in should be forbidden for the superuser
        response = self.rest_do_login("superuser", "secret3")
        content = json.loads(response.content.decode())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('token' in content, msg="There should not be a token in the response")

        # there should be zero tokens
        self.assertEqual(MultiToken.objects.all().count(), 0)

    def test_logout_with_invalid_token(self):
        """ Tries to log out with an invalid token """
        token = self.login_and_obtain_token("user1", "secret1")
        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

        # logout with an invalid token
        response = self.rest_do_logout(token + "a")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # there should be one token
        self.assertEqual(MultiToken.objects.all().count(), 1)

    def test_logout_without_token(self):
        """ Try to logout without a token """
        self.reset_client_credentials()
        response = self.rest_do_logout(None)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('drf_multitokenauth.signals.pre_auth.send')
    @patch('drf_multitokenauth.signals.post_auth.send')
    def test_signals(self, mock_pre_auth, mock_post_auth):
        """ checks whether the signal handlers are called or not"""
        # verify that signal handlers have not yet been called
        self.assertFalse(mock_pre_auth.called)
        self.assertFalse(mock_post_auth.called)

        # try login with invalid credentials
        self.rest_do_login("user1", "wrong_secret")

        # make sure the signals have not been called
        self.assertFalse(mock_pre_auth.called)
        self.assertFalse(mock_post_auth.called)

        # do a login and verify that both signals have been called
        self.rest_do_login("user1", "secret1")

        self.assertTrue(mock_pre_auth.called)
        self.assertTrue(mock_post_auth.called)

        self.assertEqual(mock_pre_auth.call_count, 1)
        self.assertEqual(mock_post_auth.call_count, 1)

