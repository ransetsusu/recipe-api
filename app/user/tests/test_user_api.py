from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_USER_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test users API public """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test creating user with valid payload is successful """
        payload = {
            'email': 'test@phdev.com',
            'password': 'testpass',
            'name': 'testname'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test creating user that already exists """
        payload = {
            'email': 'test@phdev.com',
            'password': 'testpass',
            'name': 'testname'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password must be more than 5 chars """
        payload = {
            'email': 'test@phdev.com',
            'password': 'pw',
            'name': 'asdadasdsad'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']).exists()

        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """ Test that a token will be created for user """
        payload = {
            'email': 'test@phdev.com',
            'password': 'password123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creds(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@phasdasd.com', password='testpass123')
        payload = {
            'email': 'test@phasdasd.com',
            'password': 'wrong'
        }

        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exit"""
        payload = {
            'email': 'test@phasdasd.com',
            'password': 'asdasdasd'
        }
        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """ Test that email and password are required"""
        payload = {'email': 'asd', 'password': ''}
        res = self.client.post(TOKEN_USER_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
