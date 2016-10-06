import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from eric.coreauth.models import MultiToken

# read http://www.django-rest-framework.org/api-guide/testing/ for more info about testing with django rest framework


class LoginLogoutTest(APITestCase):
    """ Extensive testing of login and logout using multitoken"""

    def setUp(self):
        """ set up a couple of users"""
        self.user1 = User.objects.create_user(
            username='johndoe', email='johndoe@mail.com', password='top_secret')

        self.user2 = User.objects.create_user(
            username='foobar', email='foo@bar.com', password='foobar')

        self.user3 = User.objects.create_user(
            username='alice', email='alice@mail.com', password='alice_secret')

        self.user4 = User.objects.create_user(
            username='bob', email='bob@mail.com', password='bob_secret')

    def set_client_credentials(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def reset_client_credentials(self):
        self.client.credentials()

    def logout_with_token(self, token, HTTP_USER_AGENT='API_TEST_CLIENT', REMOTE_ADDR='127.0.0.1'):
        """ Checks if the token exists, then log sthe user out, and checks that the token no longer exists """
        # token should be in database
        self.assertEqual(len(MultiToken.objects.filter(key=token)), 1)
        # set client credentials to the current token
        self.set_client_credentials(token)

        # call logout
        response = self.client.post('/api/auth/logout', HTTP_USER_AGENT=HTTP_USER_AGENT, REMOTE_ADDR=REMOTE_ADDR)

        # make sure the response is "logged_out"
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "{\"status\":\"logged out\"}")

        # verify the token has been deleted
        self.assertEqual(len(MultiToken.objects.filter(key=token)), 0)

    def login_and_return_token(self, username, password, HTTP_USER_AGENT='API_TEST_CLIENT', REMOTE_ADDR='127.0.0.1'):
        """ logs in and returns the token
        checks with assert calls that the login was successful (token exists, user agent and remote addr are set)
        """

        # reset auth token in header, if it exists
        self.reset_client_credentials()

        # check if the user exists
        avail_users = User.objects.filter(username=username)
        self.assertEqual(len(avail_users), 1)
        cur_user = avail_users[0]

        # login with self.user1, a given user agent and remote address
        response = self.client.post('/api/auth/login',
                                    {'username': username, 'password': password},
                                    HTTP_USER_AGENT=HTTP_USER_AGENT, REMOTE_ADDR=REMOTE_ADDR)

        # check if login was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "{\"token\":\"")

        content = json.loads(response.content.decode())
        token = content['token']

        # there should now be exactly one token
        self.assertEqual(len(MultiToken.objects.filter(key=token, user=cur_user)), 1)
        self.assertEqual(MultiToken.objects.filter(key=token, user=cur_user)[0].user_agent, HTTP_USER_AGENT)
        self.assertEqual(MultiToken.objects.filter(key=token, user=cur_user)[0].last_known_ip, REMOTE_ADDR)

        return token

    def test_login_logout_user1_success(self):
        """ Tries to login and checks if a token has been created,
        logs out after that and checks if token has been deleted"""

        # initial state: no tokens should exist
        self.assertEqual(len(MultiToken.objects.all()), 0)

        # login and get token
        token = self.login_and_return_token(self.user1.username, 'top_secret')
        # check that token is not empty
        self.assertNotEqual(token, "")
        self.assertEqual(len(MultiToken.objects.all()), 1)

        # add credentials for the logout call
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post('/api/auth/logout')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(MultiToken.objects.all()), 0)

    def test_login_logout_user1_wrong_password(self):
        """ Tries to login with a wrong password or wrong username, and checks if a token has been created.
        in the end, the login is successful with correct password."""

        # initial state: no tokens should exist
        self.assertEqual(len(MultiToken.objects.all()), 0)

        # reset auth token in header, if it exists
        self.reset_client_credentials()

        # login with self.user1 but a wrong password
        response = self.client.post('/api/auth/login',
                                    {'username': "johndoe", 'password': "top_sicret"},
                                    HTTP_USER_AGENT="TestClient", REMOTE_ADDR="127.0.0.1")

        self.assertEqual(len(MultiToken.objects.all()), 0)

        # check if login failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("Unable to log in" in response.content.decode(),
                        msg="Checking if 'Unable to log in' is in the response")

        # login with a wrong user name, but the correct password
        response = self.client.post('/api/auth/login',
                                    {'username': "john_doe", 'password': "top_secret"},
                                    HTTP_USER_AGENT="TestClient", REMOTE_ADDR="127.0.0.1")

        self.assertEqual(len(MultiToken.objects.all()), 0)

        # check if login failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("Unable to log in" in response.content.decode(),
                        msg="Checking if 'Unable to log in' is in the response")

        # login with a wrong user name, and a wrong password
        response = self.client.post('/api/auth/login',
                                    {'username': "john_doe", 'password': "top_sicret"},
                                    HTTP_USER_AGENT="TestClient", REMOTE_ADDR="127.0.0.1")

        self.assertEqual(len(MultiToken.objects.all()), 0)

        # check if login failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("Unable to log in" in response.content.decode(),
                        msg="Checking if 'Unable to log in' is in the response")

        # finally, log in with the right username and password
        response = self.client.post('/api/auth/login',
                                    {'username': "johndoe", 'password': "top_secret"},
                                    HTTP_USER_AGENT="TestClient", REMOTE_ADDR="127.0.0.1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(MultiToken.objects.all()), 1)

    def test_logout_with_wrong_token(self):
        """ Tests that logout does not work with an invalid token """
        self.assertEqual(len(MultiToken.objects.all()), 0)
        token1 = self.login_and_return_token("johndoe", "top_secret")
        self.assertEqual(len(MultiToken.objects.all()), 1)
        # add credentials for the logout call
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + "wrong token")
        response = self.client.post('/api/auth/logout')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(MultiToken.objects.all()), 1)

    def test_login_logout_multiple_times_success(self):
        """ Tries to login and checks if a token has been created,
        logs out after that and checks if token has been deleted"""

        # initial state: no tokens should exist
        self.assertEqual(len(MultiToken.objects.all()), 0)

        token1 = self.login_and_return_token(self.user1.username, 'top_secret')
        self.assertEqual(len(MultiToken.objects.all()), 1)

        token2 = self.login_and_return_token(self.user1.username, 'top_secret', REMOTE_ADDR="127.0.0.2")
        self.assertEqual(len(MultiToken.objects.all()), 2)
        # tokens should not be equal
        self.assertNotEqual(token1, token2)

        token3 = self.login_and_return_token(self.user1.username, 'top_secret', REMOTE_ADDR="127.0.0.3")
        self.assertEqual(len(MultiToken.objects.all()), 3)
        self.assertNotEqual(token1, token3)
        self.assertNotEqual(token2, token3)

        # now log out with token2
        self.logout_with_token(token2)
        # check the other two tokens still exist
        self.assertEqual(len(MultiToken.objects.all()), 2)
        self.assertEqual(len(MultiToken.objects.filter(key=token1)), 1)
        self.assertEqual(len(MultiToken.objects.filter(key=token3)), 1)

        self.logout_with_token(token1)
        self.logout_with_token(token3)

        self.assertEqual(len(MultiToken.objects.all()), 0)

