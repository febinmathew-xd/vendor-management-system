from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


#create user test 
#edge cases: duplicate username | missing username or password fields | invalid email


class TestCreateUserView(APITestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        User.objects.all().delete()
    
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
    

    def test_create_user_invalid_email(self):
        url = reverse('register')
        data = {
            'username': 'emailuser',
            'email': 'invalidemail',
            'password': '1234'
        }

        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


