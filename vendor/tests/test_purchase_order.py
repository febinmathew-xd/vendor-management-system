from rest_framework.test import APITestCase
from rest_framework import status
from ..models import PurchaseOrder, Vendor
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timedelta
import json
from django.utils import timezone



class TestPurchaseOrderView(APITestCase):

    def setUp(self) -> None:
        user = User.objects.create_user('user1', 'user1@gmail.com', 'pass123')
        self.vendor = Vendor.objects.create(user=user, name='name', contact_details= 'contact', address='address')
        self.url = reverse('purchase_order')
        token_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data= {"username": 'user1', "password": "pass123"},
            format= 'json'
        )

        self.access_token = token_response.data['access']
    

    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    

    def test_create_purchase_order_view(self):

        items = [{"product_name":"mobile", "price":20000}, {"product_name":"watch", "price": 29999}]
        json_items = json.dumps(items)

        data = {
            "vendor": self.vendor.id,
            "delivery_date": datetime.now()+ timedelta(days=3),  #3 days from order date
            "items": json_items,
            "quantity": len(items),
            "issue_date": datetime.now()
        }

        response = self.client.post(
            path=self.url,
            data=data,
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"

        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'expected status code 201.CREATED')

    
    def test_unauthorized_create_purchase_order_view(self):



        items = [{"product_name":"mobile", "price":20000}, {"product_name":"watch", "price": 29999}]
        json_items = json.dumps(items)

        data = {
            "vendor": self.vendor.id,
            "delivery_date": datetime.now()+ timedelta(days=3),  #3 days from order date
            "items": json_items,
            "quantity": len(items),
            "issue_date": datetime.now()
        }

        response = self.client.post(path=self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
    def test_invalid_data_create_purchase_order(self):

        data = {
            "vendor": self.vendor.id,
            "delivery_date": datetime.now()+ timedelta(days=3),  #3 days from order date
            "issue_date": datetime.now()
        }

        response = self.client.post(
            path=self.url,
            data=data,
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    


    def test_get_purchase_order_by_vendor_id(self):

        items = [{"product_name":"mobile", "price":20000}, {"product_name":"watch", "price": 29999}]
        json_items = json.dumps(items)

        data = {
            
            "delivery_date": timezone.now()+ timedelta(days=3),  #3 days from order date
            "items": json_items,
            "quantity": len(items),
            "issue_date": timezone.now()
        }

        for _ in range(4):
            PurchaseOrder.objects.create(vendor=self.vendor, **data)
        
        response = self.client.get(path=self.url+f"?vendor_id={self.vendor.id}", HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),4)

    

    def test_get_purchase_order_by_invalid_vendor_id(self):
        # without vendor id
        response = self.client.get(path=self.url, HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # with invalid vendor id
        response = self.client.get(path=self.url+"?vendor_id=500", HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # without authorization
        response = self.client.get(path=self.url+f"?vendor_id={self.vendor.id}" )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


         


    




