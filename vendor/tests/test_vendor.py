from ..models import Vendor
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User


# OVERVIEW
# This test module covers all tesing related to the vendor creation, retival, delete and updation operation.
# 1. TestVendorView: tests vendor creation and retrival of all vendors
# 2. GetVendorbyID : Tests retrive a specific vendor by id
# 3. UpdateVendorbyID: Tests update a specifc vendor by id
# 4. DeleteVendorbyID : Tests delete a specific vendor by id
# 5. Retive vendor performance metrics: Tests retrive performance metric of a specific vendor by id

#-------------------------------------------------------------------------------------------------------------# 

# 1. Test create a vendor and list all vendor
# Endpont : /api/vendors/
# Methods : POST, GET
class TestVendorView(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('vendors')
        self.user = User.objects.create_user('user1', 'user1@gmail.com', 'pass123')
        response = self.client.post(reverse('token_obtain_pair'), data={'username':'user1', 'password':'pass123'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']


    def tearDown(self) -> None:
        Vendor.objects.all().delete()
        User.objects.all().delete()
    
    # Test vendor creation with proper data and authorization
    def test_vendor_creation(self):

        data = {
            'user': self.user.id,
            'name': 'vendor1',
            'contact_details': 'vendor1 contact details',
            'address': 'vendor1 address',
        
        }

        response = self.client.post(path=self.url, data=data, format='json',HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # test vendor creation with unauthorized user
    def test_unauthorized_vendor_creation(self):
        data = {
            'user': self.user.id,
            'name': 'vendor1',
            'contact_details': 'vendor1 contact details',
            'address': 'vendor1 address',
        
        }
        response = self.client.post(path=self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # TEst vendor creation with invalid data
    def test_invalid_data_vendor_creation(self):
        data ={
            'name': 'user2'
        }

        response = self.client.post(path=self.url, data=data, format='json', HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # test list all vendos with authorization
    def test_get_vendors(self):
        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # test list all vendors without authorization
    def test_unauthorized_get_vendors(self):
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    

# 2. Test get vendor by id
#   Endpont: /api/vendors/{vendor_id}
#   Method : GET
class TestGetVendorByIdView(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user('user4', 'user4@gmail.com', 'pass123')
        self.vendor = Vendor.objects.create(user=self.user, name='febin', contact_details='details', address='address')
        self.url = reverse('vendor_by_id', args=[self.vendor.id])
        response = self.client.post(path=reverse('token_obtain_pair'), data={'username':'user4', 'password':'pass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']

    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
    
    def test_get_vendor_by_id(self):
        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_vendor_by_invalid_id(self):
        response = self.client.get(path=reverse('vendor_by_id', args=[23]), HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_vendor_by_id_unauthorized(self):
        respone = self.client.get(path=self.url)
        self.assertEqual(respone.status_code, status.HTTP_401_UNAUTHORIZED)

#-----------------------------------------------------------------------------------------------#

#3. Test Vendor update by Id

# Method: PUT
# endpoint: /api/vendors/{vendor_id}/

class TestUpdateVendorByIdView(APITestCase):
    
    def setUp(self) -> None:
        self.user = User.objects.create_user('user7', 'user7@gmail.com', 'pass123')
        self.vendor = Vendor.objects.create(user=self.user, name='sample name', contact_details='sample details', address='sample address')
        self.url = reverse('vendor_by_id', args=[self.vendor.id])

        # obtain the access token for the user
        response = self.client.post(path=reverse('token_obtain_pair'), data={'username':'user7', 'password': 'pass123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']

        

    
    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
    

    def test_put_vendor_by_id(self):
        """
        Testing put method using valid data, valid vendor id and authenticated user
        Expected response status 200.OK
        """
        data ={
            'name':'changed name',
            'address': 'changed address'
        }
        response = self.client.put(path=self.url, data=data, format='json', HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_put_vendor_by_invalid_id(self):
        """
        test put method using invalid vendor id, expected response status 404.NOT_FOUND
        """
        data ={
            'name':'changed name',
            'address': 'changed address'
        }

        response = self.client.put(path=reverse('vendor_by_id', args=[23]), data=data, format='json', HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_put_vendor_by_id_invalid_data(self):
        """
        test update vendor using invalid data parameter
        """

        data ={
            'name': 1345
        }
        response = self.client.put(path=self.url, data=data, format='json', HTTP_AUTHORIZATION= f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_put_vendor_by_id(self):
        """
        test put method by an unauthorized user. Expected response status 401 UNAUTHORIZED
        """

        data ={
            'name':'changed name',
            'address': 'changed address'
        }

        response = self.client.put(path=self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_non_onwer_put_vendor_by_id(self):

        data ={
            'name':'changed name',
            'address': 'changed address'
        }

        user = User.objects.create_user('nonuser', 'nonuser@gmail.com', 'pass123')
        token_res = self.client.post(path=reverse('token_obtain_pair'), data={"username":"nonuser", "password":"pass123"}, format='json')
        access = token_res.data['access']
        response = self.client.put(path=self.url, data=data, format='json', HTTP_AUTHORIZATION= f"Bearer {access}")
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        


#-----------------------------------------------------------------------------------------------------------------------------------------#

#4. Test DELETE vendor by id
# Method: DELETE
# endpoint: /api/vendors/{vendor_id}/

class TestDeleteVendorByIdView(APITestCase):

    def setUp(self) -> None:
        user = User.objects.create_user('user11', 'user11@gmail.com', 'pass123')
        vendor = Vendor.objects.create(user=user, name='name', contact_details='contact', address='address')
        response = self.client.post(path=reverse('token_obtain_pair'), data={"username":"user11", "password":"pass123"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']
        self.url = reverse('vendor_by_id', args=[vendor.id])

    
    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()

    
    def test_delete_vendor_by_id(self):
        """
        test delete vendor by id with proper vendor id and authorizathon.
        expected response status 200.OK
        """

        response = self.client.delete(path=self.url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK, "expected response 200.OK")
    
    
    def test_delete_vendor_by_invalid_id(self):
        """
        test delete vendor by providing invalid vendor id: expected response status 404.NOT_FOUND
        """

        response = self.client.delete(
            path= reverse('vendor_by_id', args=[35]), #invalid vendor id
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            'expected status code 404_NOT_FOUND'
        )
    

    def test_unauthorized_delete_vendor_by_id(self):
        """
        test delete vendor by unauthorized user(other than original user)
        """

        user = User.objects.create_user(
            'test',
            'test@gmail.com',
            'pass123'
        )
        token_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data={"username": "test", "password": "pass123"},
            format='json'
        )

        self.assertEqual(token_response.status_code,  status.HTTP_200_OK)
        access_token = token_response.data['access']
        response = self.client.delete(
            path=self.url,
            HTTP_AUTHORIZATION= f"Bearer {access_token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            'expected status code 403 FORBIDDEN'
        )


    def test_unauthenticated_delete_vendor_by_id(self):
        """
        test delete vendor by a not authenticated user(anonymous user).
        expected status code 401 UNAUTHORIZED
        """

        response = self.client.delete(path=self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            'expected status code 401 UNAUTHORIZED'
        )
    


# 5. test vendor performance metrics retrival by vendor ID
# method GET
# endpoint /api/vendors/{vendor_id}/performance/
# 
# Test cases: 
# 1. test with proper data
# 2. test with unauthorized user
# 3. test with invalid vendor id

class TestVendorPerformanceMetrics(APITestCase):

    def setUp(self) -> None:
        user = User.objects.create_user('test', 'test@mail.com', 'pass123')
        self.vendor = Vendor.objects.create(
            user=user,
            name='name',
            contact_details='contact',
            address='address'
        )
        token_response = self.client.post(
            path= reverse('token_obtain_pair'),
            data={
                "username": "test",
                "password": "pass123"
            },
            format='json'
        )
        self.access_token = token_response.data['access']
        self.url = reverse('performance_metrics', args=[self.vendor.id])
    

    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
    

    # 1. Test with proper data and authorization
    # expected status code 200.OK
    # response data: complete performance metrics of the given vendor

    def test_get_performance_metrics(self):

        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 2. Test unauthorized performance GET request
    # expected status code 401 UNAUTHORIZED
    # response data: error

    def test_get_performance_metrics_unauthorized(self):
        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # 3. Test GET performance matrics with invalid vendor ID
    # expected status code 404.NOT_FOUND
    # response data: error

    def test_get_performance_metrics_invalid_id(self):
        response =self.client.get(
            path=reverse('performance_metrics', args=[312]), # invalid ID
            HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



