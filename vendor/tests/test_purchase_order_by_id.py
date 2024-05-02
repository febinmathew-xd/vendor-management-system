from rest_framework.test import APITestCase
from rest_framework import status
from ..models import Vendor, PurchaseOrder
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta



class TestGetPurchaseOrderById(APITestCase):

    def setUp(self) -> None:
        user = User.objects.create_user('user1', 'user1@gmail.com', 'pass123')
        vendor = Vendor.objects.create(user=user, name= 'name', contact_details='contact', address='address')
        token_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data= {'username':'user1', 'password': 'pass123'},
            format='json'
        )
        
        self.access_token = token_response.data['access']
        self.purchase_order = PurchaseOrder.objects.create(
            vendor=vendor,
            order_date = timezone.now(),
            delivery_date= timezone.now() + timedelta(days=4),
            items = [{'product':'product1'}, {'product': 'product2'}],
            quantity = 2,
            issue_date = timezone.now()

        )
        self.url = reverse('purchase_order_by_id', args=[self.purchase_order.id])

    
    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    

    def test_get_purchase_order_by_id(self):

        response = self.client.get(
            path=self.url,
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_update_purchase_order_by_id(self):

        data = {
            'status': 'completed',
            'quality_rating': 4.6
        }

        response = self.client.put(
            path= self.url,
            data= data,
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], data['status'])
        self.assertEqual(response.data['quality_rating'], data['quality_rating'])
    

    def test_update_purchase_order_invalid_data(self):

        data = { 'quality_rating': 'rejf'}
        response = self.client.put(
            path= self.url,
            data=data,
            format= 'json',
            HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_purchase_order_by_invalid_id(self):

        # test GET method for invalid id
        response = self.client.get(
            path= reverse('purchase_order_by_id', args=[34]), #invalid order id
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # test PUT method for invalid id
        response = self.client.put(
            path= reverse('purchase_order_by_id', args=[34]), #invalid order id
            data= {"quality_rating": 3.5},
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # test DELETE method for invalid id
        response = self.client.delete(
            path= reverse('purchase_order_by_id', args=[34]), #invalid order id
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    

    def test_unauthorized_purchase_order_by_id(self):
        
        # test GET method for unauthorized user
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test PUT method for unauthorized user
        response = self.client.put(
            path=self.url,
            data={"quality_rating": 2.5},
            format= 'json'    
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test DELETE method for unauthorized user
        response = self.client.delete(path=self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        


    
    def test_purchase_order_by_id_other_user(self):
        
        
        User.objects.create_user('user2', 'user2@gmail.com', 'pass123')
        token_response = self.client.post(path=reverse('token_obtain_pair'), data={"username": "user2", "password": "pass123"})
        access = token_response.data['access']

        # test GET method called by other user
        response = self.client.get(
            path= self.url,
            HTTP_AUTHORIZATION = f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test PUT method called by other user
        response = self.client.put(
            path= self.url,
            data= {"quality_rating": 3.5},
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
  
        # test DELETE method called by other user
        response = self.client.delete(
            path= self.url,
            HTTP_AUTHORIZATION = f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    
    def test_delete_purchase_order_by_id(self):

        response = self.client.delete(path=self.url, HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    