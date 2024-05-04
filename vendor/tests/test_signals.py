from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import Vendor, PurchaseOrder
from django.utils import timezone
from rest_framework import status
from django.urls import reverse
from datetime import timedelta




class TestQualityRatingSignals(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user('test','test@mail.com', 'pass123')
        self.vendor = Vendor.objects.create(
            user=self.user,
            name='name',
            contact_details='contact',
            address= 'address'
        )
        self.items = [{"product_name": "mobile"}, {"product_name": "watch"}]
        token_response = self.client.post(
            path= reverse('token_obtain_pair'),
            data={"username": "test", "password":"pass123"},
            format='json'
        )
        self.access_token = token_response.data['access']
        self.purchase_order = PurchaseOrder.objects.create(
            vendor=self.vendor,
            delivery_date=timezone.now() + timedelta(days=4),
            items=self.items,
            quantity= len(self.items),
            issue_date = timezone.now() - timedelta(hours=3)

        )
        self.data = {"delivery_date": timezone.now()+ timedelta(days=4), "items": self.items, "quantity": len(self.items), "issue_date": timezone.now()-timedelta(hours=3)}
    
    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    

    def test_is_quality_rating_changed(self):
        self.client.put(
            path= reverse('purchase_order_by_id', args=[self.purchase_order.id]),
            data= {"quality_rating": 3.9},
            format='json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        po = PurchaseOrder.objects.get(id=self.purchase_order.id)
        self.assertEqual(po.quality_rating, 3.9)
        vendor = Vendor.objects.get(id=self.vendor.id)
        self.assertEqual(vendor.quality_rating_avg, 3.9)

        # Test if modify already existing quality rating(not None)
        # expected behaviour: recalculate and modify vendor's quality rating average effectively
        self.client.put(
            path= reverse('purchase_order_by_id', args=[self.purchase_order.id]),
            data= {"quality_rating": 4.6},
            format = 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        po = PurchaseOrder.objects.get(id=self.purchase_order.id)
        vendor = Vendor.objects.get(id=self.vendor.id)
        self.assertEqual(po.quality_rating, 4.6)
        self.assertEqual(vendor.quality_rating_avg, 4.6)
    

    def test_quality_rating_provided_all(self):
        ratings = [1.0, 2.0, 3.0, 4.0]
        for i in range(len(ratings)):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.put(
                path= reverse('purchase_order_by_id', args=[purchase_order.id]),
                data= {"quality_rating": ratings[i]},
                format = 'json',
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        vendor = Vendor.objects.get(id=self.vendor.id)
        self.assertEqual(vendor.quality_rating_avg, sum(ratings)/len(ratings))
    

    def test_with_missing_quality_rating(self):

        for _ in range(6):
            PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
    
        ratings = [1.0, 2.0, 3.0, 4.0]
        for i in range(len(ratings)):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.put(
                path= reverse('purchase_order_by_id', args=[purchase_order.id]),
                data= {"quality_rating": ratings[i]},
                format = 'json',
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        vendor = Vendor.objects.get(id=self.vendor.id)
        self.assertEqual(vendor.quality_rating_avg, sum(ratings)/len(ratings))
    

    def test_modify_existing_quality_rating(self):

        ratings = [1.0, 2.0, 3.0, 4.0, 5.0]
        purchase_ids = []
        for i in range(len(ratings)):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            purchase_ids.append(purchase_order.id)
            response = self.client.put(
                path= reverse('purchase_order_by_id', args=[purchase_order.id]),
                data= {"quality_rating": ratings[i]},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertEqual(PurchaseOrder.objects.get(id=purchase_order.id).quality_rating, ratings[i])
            average = sum(ratings[:i+1])/(i+1)
            self.assertEqual(Vendor.objects.get(id=self.vendor.id).quality_rating_avg, average)
        
        final_avg= sum(ratings)/len(ratings)
        self.assertEqual(Vendor.objects.get(id=self.vendor.id).quality_rating_avg,final_avg )

        self.assertEqual(len(ratings), len(purchase_ids)) # make sure stored all IDs

        # add some non rated purchase order
        for _ in range(5):
            PurchaseOrder.objects.create(vendor=self.vendor, **self.data)

        # modify existing rating with new rating value
        new_ratings = [6.0, 7.0, 8.0, 9.0, 10.0]

        for i in range(len(purchase_ids)):
            response = self.client.put(
                path=reverse('purchase_order_by_id', args=[purchase_ids[i]]),
                data={"quality_rating": new_ratings[i]},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(PurchaseOrder.objects.get(id=purchase_ids[i]).quality_rating, new_ratings[i])
            inter_ratings = ratings[i+1:] + new_ratings[:i+1]
            self.assertEqual(
                Vendor.objects.get(id=self.vendor.id).quality_rating_avg,
                sum(inter_ratings)/len(inter_ratings)
            ) 
        
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).quality_rating_avg,
            sum(new_ratings)/len(new_ratings)
        )
    

    def test_other_field_updation_affects(self):

        ratings = [1.0, 2.0, 3.0, 4.0]

        for i in range(len(ratings)):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.put(
                path=reverse('purchase_order_by_id', args=[purchase_order.id]),
                data= {"quality_rating": ratings[i]},
                format= 'json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        non_rated_purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
        response = self.client.put(
            path=reverse('purchase_order_by_id', args=[non_rated_purchase_order.id]),
            data= {"status":"completed"},
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PurchaseOrder.objects.get(id=non_rated_purchase_order.id).status, "completed")
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).quality_rating_avg,
            sum(ratings)/len(ratings)
        )
    


class TestOnTimeDeliveryRate(APITestCase):
    
    def setUp(self) -> None:
        user = User.objects.create_user('test', 'test@mail.com', 'pass123')
        self.vendor = Vendor.objects.create(user=user, name='name', contact_details='contact', address='address')
        self.data = {
            'items': [{"name":"mobile"}, {"name":"watch"}],
            'quantity': 2,
            'issue_date': timezone.now() -timedelta(hours=3)
        }
        response_token = self.client.post(
            path= reverse('token_obtain_pair'),
            data={"username":"test", "password":"pass123"},
            format= 'json'
        )
        self.access_token = response_token.data['access']
        self.reverse_name = 'purchase_order_by_id'
    

    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    

    # Test on or before delivery

    def test_on_time_delivery(self):

        delivery_dates = []
        for i in range(1,5):
            delivery_dates.append(timezone.now()+timedelta(days=i))
        
        on_time_delivery_count_list = []

        for i in range(len(delivery_dates)):
            if delivery_dates[i] > timezone.now():
                on_time_delivery_count_list.append(1)
            else:
                on_time_delivery_count_list.append(0)

        
        purchase_order_ids =[]
        for i in range(len(delivery_dates)):
            purchase_order = PurchaseOrder.objects.create(
                vendor= self.vendor,
                delivery_date= delivery_dates[i],
                **self.data
            )
            purchase_order_ids.append(purchase_order.id)
        
        # add some non completed purchase orders
        for _ in range(6):
            PurchaseOrder.objects.create(
                vendor=self.vendor,
                delivery_date = timezone.now()+timedelta(5),
                **self.data
            )
        
        # add some canceled purchase order
        for _ in range(4):
            PurchaseOrder.objects.create(
                vendor=self.vendor,
                delivery_date = timezone.now()+ timedelta(2),
                status = "canceled",
                **self.data
            )
        
        for i in range(len(purchase_order_ids)):
            response = self.client.put(
                path=reverse(self.reverse_name, args=[purchase_order_ids[i]]),
                data= {"status": "completed"},
                format = 'json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                PurchaseOrder.objects.get(id=purchase_order_ids[i]).status,
                "completed"
            )
            self.assertEqual(
                Vendor.objects.get(id=self.vendor.id).on_time_delivery_rate,
                sum(on_time_delivery_count_list[:i+1])/len(on_time_delivery_count_list[:i+1])
            )
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).on_time_delivery_rate,
            sum(on_time_delivery_count_list)/len(on_time_delivery_count_list),
            'expected ontime delivery same as calculated value'
        )     


    # Test mixed delivery dates

    def test_on_and_after_delivery_date(self):

        on_time_dates = []
        after_time_dates = []

        for i in range(1,6):
            on_time_dates.append(timezone.now()+timedelta(days=i))
            after_time_dates.append(timezone.now()-timedelta(days=i))
        
        all_dates = on_time_dates + after_time_dates

        date_count_ref_list =[]

        for i in range(len(all_dates)):
            if all_dates[i] > timezone.now():
                date_count_ref_list.append(1)
            else:
                date_count_ref_list.append(0)
        
        # add some non delivered purchase orders
        for _ in range(6):
            PurchaseOrder.objects.create(
                vendor=self.vendor,
                delivery_date = timezone.now()+ timedelta(days=7),
                **self.data
            )
        # add some canceled purchase order
        for _ in range(6):
            PurchaseOrder.objects.create(
                vendor=self.vendor,
                delivery_date= timezone.now()+ timedelta(2),
                status= 'canceled',
                **self.data
            )
        

        for i in range(len(all_dates)):
            purchase_order = PurchaseOrder.objects.create(
                vendor=self.vendor,
                delivery_date = all_dates[i],
                **self.data
            )
            
            response = self.client.put(
                path=reverse(self.reverse_name, args=[purchase_order.id]),
                data= {"status": "completed"},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertAlmostEquals(
                Vendor.objects.get(id=self.vendor.id).on_time_delivery_rate,
                sum(date_count_ref_list[:i+1])/len(date_count_ref_list[:i+1]),
                places=2
            )
        
        self.assertAlmostEquals(
            Vendor.objects.get(id=self.vendor.id).on_time_delivery_rate,
            sum(date_count_ref_list)/len(date_count_ref_list),
            places=2
        )
    

    def test_other_field_updation_affects(self):

        purchase_order = PurchaseOrder.objects.create(
            vendor= self.vendor,
            delivery_date= timezone.now() + timedelta(days=3),
            **self.data
        )
        response = self.client.put(
            path= reverse(self.reverse_name, args=[purchase_order.id]),
            data={"status": "completed"},
            format ='json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(
            path= reverse(self.reverse_name, args=[purchase_order.id]),
            data= {"quality_rating":3.4},
            format= 'json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(Vendor.objects.get(id=self.vendor.id).on_time_delivery_rate, 1.0)




class TestFulfillmentRate(APITestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

