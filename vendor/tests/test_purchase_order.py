from rest_framework.test import APITestCase
from rest_framework import status
from ..models import Vendor, PurchaseOrder
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime
import json


# OVERVIEW
# All the test cases for the model Purchase order is covered in this test module
# This test module includes three TestCase classes
# 1. Test create Purchase order and list all purchase order with an option to filter by vendor
# 2. Test operation on a specific purchase order by providing its ID
# 3. Test acknowledge purchase order by vendor


#-------------------------------------------------------------------------------#


# 1. Test create Purchase order and list all purchase order with an option to filter by vendor
# endpoints:
# - POST /api/purchase_orders/
# - GET /api/purchase_orders/


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
    
    # Test create purchase order by providing proper data
    # endpoint POST /api/purchase_orders/
    # expected status code 201.CREATED
    # response data: all data of created purchase order
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

    # Test create purchase order by an unauthorized user
    # endpoint POST /api/purchase_orders/
    # expected status code 401.UNAUTHORIZED
    # response data: error
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

    # Test create purchase order by providing invalid data
    # endpoint POST /api/purchase_orders/
    # expected status code 400.BAD_REQUEST
    # response data: error
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
    

    # Test get purchase order by valid vendor ID
    # endpoint GET /api/purchase_orders/
    # expected status code 200.OK
    # response data: all purchase order details of the provided vendor ID
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

    
    # Test get purchase order without any vendor ID , with invalid vendor ID and by an unauthorized user
    # endpoint GET /api/purchase_orders/
    # expected status code 400.BAD_REQUEST/ 404.NOT_FOUND/ 4O1.UNAUTHORIZED
    # response data: error
    def test_get_purchase_order_by_invalid_vendor_id(self):

        # without vendor id
        # expected status code 400.BAD_REQUEST
        response = self.client.get(path=self.url, HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # with invalid vendor id
        # expected status code 404.NOT_FOUND
        response = self.client.get(path=self.url+"?vendor_id=500", HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # without authorization
        # expected status code 4O1.UNAUTHORIZED
        response = self.client.get(path=self.url+f"?vendor_id={self.vendor.id}" )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)




#---------------------------------------------------------------------------------------------------------------#
  




# 2. Test operation on a specific purchase order by providing its ID
# endponts:
# - GET /api/purchase_orders/{purchase_order_id}/
# - PUT /api/purchase_orders/{purchase_order_id}/
# - DELETE /api/purchase_orders/{purchase_order_id}/

# Test Cases:
# 1. Test with proper purchase order ID
# 2. Test with invalid purchase order ID
# 3. Test unauthorized user requests
# 4. Test non owner user request to perform PUT and DELETE methods

class TestPurchaseOrderById(APITestCase):

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
    
    # Test retrive a specific purchase order by ID
    # endpoint GET /api/purchase_orders/{purchase_order_id}/
    # expected status code 200.OK
    def test_get_purchase_order_by_id(self):

        response = self.client.get(
            path=self.url,
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # Test update a specific purchase order by ID
    # endpoint PUT /api/purchase_orders/{purchase_order_id}/
    # expected status code 200.OK
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
        # make sure the value updated properly
        self.assertEqual(response.data['status'], data['status'])
        self.assertEqual(response.data['quality_rating'], data['quality_rating']) 
    
    # Test update purchase order by providing invalid data.
    # expected status code 401.BAD_REQUEST
    def test_update_purchase_order_invalid_data(self):

        data = { 'quality_rating': 'rejf'} # invalid data
        response = self.client.put(
            path= self.url,
            data=data,
            format= 'json',
            HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # Test GET, PUT ,DELETE methods by providing invalid ID
    #expected status code 404.NOT_FOUND
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

    
    # Test GET PUT DELETE methods performs by unauthorized users
    # expected status code 401.UNAUTHORIZED
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

    # Test non owner user requests to perform PUT and DELETE methods
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

    # Test delete a specific purchase order by ID
    #expected status code 200.OK
    def test_delete_purchase_order_by_id(self):

        response = self.client.delete(path=self.url, HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
#--------------------------------------------------------------------------------------------#



# 2. Test acknowledge purchase order by vendor
# method POST
# end point /api/purchase_orders/{purchase_order_id}/acknowledge/
#
# Test Cases:
# 1. Test with correct vendor of the purchase order 
#    - test in initial state.(no acknowledged purchase orders)
#    - test when already have multiple acknowledged purchase orders
# 2. Test with unauthorized user
# 3. Test with non owner(vendor) of the purchase order
# 4. Test with invalid purchase order ID (non existing ID)

class TestAcknowledgePurchaseOrder(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user('user4', 'user4@mail.com', 'pass123')
        self.vendor = Vendor.objects.create(
            user=self.user,
            name= 'name',
            contact_details='contact',
            address= 'address'
        )
    
        self.items = [{"name":"phone", "price": 39999}, {"name": "watch", "price": 3999}]
        token_response = self.client.post(
            path= reverse('token_obtain_pair'),
            data= {'username': 'user4', 'password': 'pass123'},
            format= 'json'
        )
        self.access_token = token_response.data['access']
    
    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    
    # Test acknowledge by correct owner of the purchase order- initial state
    def test_first_acknowledgement(self):
        issue_time = timezone.now()-timedelta(hours=5)

        purchase_order= PurchaseOrder.objects.create(
            vendor=self.vendor,
            order_date = issue_time,
            delivery_date = timezone.now() + timedelta(days=3),
            items = self.items,
            quantity = len(self.items),
            issue_date = issue_time
            )

        response = self.client.post(
            path= reverse('acknowledge_purchase_order', args=[purchase_order.id]),
            HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(PurchaseOrder.objects.get(id=purchase_order.id).acknowledgment_date, 'acknowledgement date should not be None')
        self.assertNotEqual(
            self.vendor.average_response_time,
            Vendor.objects.get(id=self.vendor.id).average_response_time,
            'expected average response rate changed from zero to new value'
        )
    
    # Test acknowledge by correct owner of the purchase order - multiple acknowledged purchase order
    def test_multiple_acknowledged_purchase_order(self):
  
        for i in range(1,5):
            purchase_order= PurchaseOrder.objects.create(
                vendor = self.vendor,
                delivery_date= timezone.now()+timedelta(days=3),
                items=[{'product_name':'mobile'}, {'product_name':'watch'}],
                quantity = 2,
                issue_date= timezone.now()-timedelta(hours=i)   #different issue date
                ) 
           
            response = self.client.post(
                path= reverse('acknowledge_purchase_order',args=[purchase_order.id] ),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
               )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # check the acknowledge date change from None to new value
            self.assertIsNotNone(PurchaseOrder.objects.get(id=purchase_order.id).acknowledgment_date)

            # calculate average at the current point to match with changed average response time
            sum = 0
            cur = i
            while cur > 0:
                sum += cur
                cur -=1
            avg = sum/i
            
            self.assertAlmostEquals(avg, Vendor.objects.get(id=self.vendor.id).average_response_time)
        # check average response time calculated properly
        self.assertEqual(Vendor.objects.get(id=self.vendor.id).average_response_time, 10/4)
               
    # Test acknowledge purchase order by an unauthorized user and by a non-owner user
    # also by providing an invalid purchase order ID
    # expected response: Error    
    def test_not_allowed_acknowledged_purchase_order(self):

        purchase_order = PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now()+ timedelta(days=4),
            items=[{'name':'phone'}, {'name': 'watch'}],
            quantity=2,
            issue_date=timezone.now()
        )
        # test if user is not authenticated
        response = self.client.post(path=reverse('acknowledge_purchase_order', args=[purchase_order.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # test if user is not the owner of the purchase order
        # expected stauts code 403 FORBIDDEN
        
        User.objects.create_user('temp', 'temp@mail.com', 'pass123') # create another user
        token_response = self.client.post(                           # obtain access token for new user
            path= reverse('token_obtain_pair'),
            data={"username": "temp", "password": "pass123"},
            format='json'
        )
        access = token_response.data['access']

        # try to acknowledge purchase order by newly created user(not owner)
        response = self.client.post(
            path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
            HTTP_AUTHORIZATION= f"Bearer {access}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            'expected status code 403_FORBIDDEN'
        )
        
        # test if invalid purchase order ID is provided

        response = self.client.post(
            path=reverse('acknowledge_purchase_order', args=[65]),  # invalid purchase order ID 
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            'expected status code 404 NOT FOUND'
        )