import json
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.test import APITestCase
from django_rest_multitokenauth.models import MultiToken, ResetPasswordToken

# try getting reverse from django.urls
try:
    # Django 1.10 +
    from django.urls import reverse
except:
    # Django 1.8 and 1.9
    from django.core.urlresolvers import reverse


reset_password_token_signal_call_count = 0
last_reset_password_token = ""

def count_reset_password_token_signal(reset_password_token, *args, **kwargs):
    global reset_password_token_signal_call_count, last_reset_password_token
    reset_password_token_signal_call_count += 1
    last_reset_password_token = reset_password_token


class HelperMixin:
    """
    Mixin which encapsulates methods for login, logout, request reset password and reset password confirm
    """
    def setUpUrls(self):
        """ set up urls by using djangos reverse function """
        self.login_url = reverse('multi_token_auth:auth-login')
        self.logout_url = reverse('multi_token_auth:auth-logout')
        self.reset_password_request_url = reverse('multi_token_auth:auth-reset-password-request')
        self.reset_password_confirm_url = reverse('multi_token_auth:auth-reset-password-confirm')

    def set_client_credentials(self, token):
        """ set client credentials, namely the auth token """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def reset_client_credentials(self):
        """ reset all client credentials """
        self.client.credentials()

    def rest_do_login(self, username, password, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        """ REST API Wrapper for login """
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

    def rest_do_request_reset_token(self, email, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        """ REST API wrapper for requesting a password reset token """
        data = {
            'email': email
        }

        return self.client.post(
            self.reset_password_request_url,
            data,
            format='json',
            HTTP_USER_AGENT=HTTP_USER_AGENT,
            REMOTE_ADDR=REMOTE_ADDR
        )

    def rest_do_reset_password_with_token(self, token, new_password, HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        """ REST API wrapper for requesting a password reset token """
        data = {
            'token': token,
            'password': new_password
        }

        return self.client.post(
            self.reset_password_confirm_url,
            data,
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

    def login_and_obtain_token(self, username, password,  HTTP_USER_AGENT='', REMOTE_ADDR='127.0.0.1'):
        response = self.rest_do_login(username, password, HTTP_USER_AGENT, REMOTE_ADDR)
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

    def test_reset_password(self):
        """ Tests resetting a password """

        # there should be zero tokens
        self.assertEqual(ResetPasswordToken.objects.all().count(), 0)

        # we need to check whether the signal is getting called
        global reset_password_token_signal_call_count
        reset_password_token_signal_call_count = 0

        from django_rest_multitokenauth.signals import reset_password_token_created
        reset_password_token_created.connect(count_reset_password_token_signal)

        response = self.rest_do_request_reset_token(email="user1@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reset_password_token_signal_call_count, 1)
        self.assertNotEqual(last_reset_password_token, "")

        # there should be one token
        self.assertEqual(ResetPasswordToken.objects.all().count(), 1)

        # if the same user tries to reset again, the user will get the same token again
        response = self.rest_do_request_reset_token(email="user1@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reset_password_token_signal_call_count, 2)
        self.assertNotEqual(last_reset_password_token, "")

        # there should be one token
        self.assertEqual(ResetPasswordToken.objects.all().count(), 1)
        # and it should be assigned to user1
        self.assertEqual(
            ResetPasswordToken.objects.filter(key=last_reset_password_token.key).first().user.username,
            "user1"
        )

        # try to reset the password
        response = self.rest_do_reset_password_with_token(last_reset_password_token.key, "new_secret")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # there should be zero tokens
        self.assertEqual(ResetPasswordToken.objects.all().count(), 0)

        # try to login with the old username/password (should fail)
        response = self.rest_do_login("user1", "secret1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # try to login with the new username/Password (should work)
        response = self.rest_do_login("user1", "new_secret")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_multiple_users(self):
        """ Checks whether multiple password reset tokens can be created for different users """
        # connect signal
        # we need to check whether the signal is getting called
        global reset_password_token_signal_call_count, last_reset_password_token
        reset_password_token_signal_call_count = 0

        from django_rest_multitokenauth.signals import reset_password_token_created
        reset_password_token_created.connect(count_reset_password_token_signal)

        # create a token for user 1
        response = self.rest_do_request_reset_token(email="user1@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResetPasswordToken.objects.all().count(), 1)
        token1 = last_reset_password_token

        # create another token for user 2
        response = self.rest_do_request_reset_token(email="user2@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tokens = ResetPasswordToken.objects.all()
        self.assertEqual(tokens.count(), 2)
        token2 = last_reset_password_token

        # validate that those two tokens are different
        self.assertNotEqual(tokens[0].key, tokens[1].key)

        # try to request another token, there should still always be two keys
        response = self.rest_do_request_reset_token(email="user1@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResetPasswordToken.objects.all().count(), 2)

        # create another token for user 2
        response = self.rest_do_request_reset_token(email="user2@mail.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ResetPasswordToken.objects.all().count(), 2)

        # try to reset password of user2
        response = self.rest_do_reset_password_with_token(token2.key, "secret2_new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # now there should only be one token left (token1)
        self.assertEqual(ResetPasswordToken.objects.all().count(), 1)
        self.assertEqual(ResetPasswordToken.objects.filter(key=token1.key).count(), 1)

        # user 2 should be able to login with "secret2_new" now
        self.login_and_obtain_token("user2", "secret2_new")

        # try to reset again with token2 (should not work)
        response = self.rest_do_reset_password_with_token(token2.key, "secret2_fake_new")
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

        # user 2 should still be able to login with "secret2_new" now
        self.login_and_obtain_token("user2", "secret2_new")



