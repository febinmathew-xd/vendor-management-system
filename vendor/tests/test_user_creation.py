from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


# OVERVIEW
# This test module inclues all the test cases for the User model and its authentication(simple JWT authentication)
# This module have two TestCase classes
# 1. Test user creation
# 2. Test simple JWT authentication


#--------------------------------------------------------------------------------------------------------------------#


# 1. Test user creation
# endpont POST /api/user/register/
# Test Cases:
# - Test by providing valid credentials
# - Test with missing credentials
# - Test with duplicate username
# - Test with invalid email

class TestCreateUserView(APITestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        User.objects.all().delete()
    
    # test user creation with valid credentials
    # exptected status code 201.CREATED
    # response data: all details of the created user
    def test_create_user_success(self):
        
        url = reverse('register')
        
        data = {
            'username': 'abcd',
            'password': 1234,
            'email': 'abcd@gamil.com'
        }

        response = self.client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='abcd').exists())

    # test user creation with duplicate usename
    # exptected status code 400.BAD_REQUEST
    # response data: error
    def test_create_user_duplicate_username(self):
        User.objects.create_user('user1', 'user1@gmail.com', '123')
        url = reverse('register')
        data = {
            'username': 'user1',  #duplicate username
            'email': 'random@gmail.com',
            'password': 'password123'
        }

        response = self.client.post(path=url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # test user creation with missing username or password
    # exptected status code 400.BAD_REQUEST
    # response data: error
    def test_create_user_missing_username_or_password(self):
        url = reverse('register')
        data1 = {
            "username": "missingpass"
        }
        data2 = {
            "password": 'missingusername'
        }

        response1 = self.client.post(path=url, data=data1, format='json')
        response2 = self.client.post(path=url, data=data2, format='json')

        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    # test user creation with invalid email
    # exptected status code 400.BAD_REQUEST
    # response data: error
    def test_create_user_invalid_email(self):
        url = reverse('register')
        data = {
            'username': 'emailuser',
            'email': 'invalidemail',
            'password': '1234'
        }

        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



#---------------------------------------------------------------------------------------------#


# 2. Test simple JWT Authentication
# endpoint POST /api/token/
# Test cases:
# - test with valid credentials
# - test with invalid credentials


class TestSimpleJWTAuthentication(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user('test', 'test@gamil.com', 'pass123')
        self.url = reverse('token_obtain_pair')
    
    def tearDown(self) -> None:
        User.objects.all().delete()
    
    # Test auth with valid credentials
    # expected status code 200.OK
    # response data: access token and refresh token
    def test_auth_valid_credentials(self):
        response = self.client.post(
            path=self.url,
            data={"username":"test", "password": "pass123"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Test auth with invalid credentials
    # expected status code 401.UNAUTHORIZED
    # response data: error
    def test_auth_invalid_credentials(self):
        # invalid username
        data = {
            "username": "invalid",
            "password": "pass123"
        }
        response = self.client.post(path=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # invalid password
        data = {"username": "test", "password": "345"}
        response = self.client.post(path=self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
