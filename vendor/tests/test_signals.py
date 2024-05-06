from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import Vendor, PurchaseOrder
from django.utils import timezone
from rest_framework import status
from django.urls import reverse
from datetime import timedelta

# OVERVIEW
# Test cases in this module covers all the tests related to the signal handler which used to handle the 
# real time calculation of the vendor performance metrics
# This module includes four test classes
# 1. Test Quality Rating Average : which cover all tests related to the realtime calculation and updation of the
#    quality rating average of the vendor when ever the quality rating field of the purchase order gets updates
# 2. Test Average Response Time: which covers all tests ralated to the real time calculation and updation of the 
#    average response time of the vendor when ever a vendor acknowledge purchase order.
# 3. Test fulfullment Rate : covers all tests ralated to the calculation and updation of fulfillment rate of the 
#    vendor when ever the status of the purchase order changes to completed or canceled.
# 4. Test Metrics When Purchase Order Deleted : covers all tests related to the accurate calculation of all the metrics
#    of the vendor when a purchase order which used to calculate current metrics gets deleted.
#    tests post_delete signal properly recalculate and update metrics accurately.

#---------------------------------------------------------------------------------------------------------------------------#


# 1. Test Quality Rating average Metrics gets calculated when ever a quality rating is provided to a purchase order
            
class TestQualityRatingSignal(APITestCase):

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
    
    # test average quility rating of the vendor changes when a quality rating of any purchase order of the vendor changes
    # expected behaviour: purchase order signal handler function trigers properly and updates quality rating average
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
    
    # test quality rating average updated corectly when all the purchase order has valid rating
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
    
    # test quality rating average updates properly even any non rated purchase order exists.
    # only calculate quality rating if provided..doesnot count all completed purchase order as total ratings.
    def test_with_missing_quality_rating(self):
        #add non rated purchase order
        for _ in range(6):
            PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
        
        # add purchase order and update quality ratings for all instance
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
    
    # prpoper calculation if an existing quality rating modified. replace old with new and recalculate metrics.
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
    
    # check if any other field which is not required for the calculation of the metrics changes not triger
    # metrics calculation
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
    

# 2. Test on time delivery rate metrics
class TestOnTimeDeliveryRateSignal(APITestCase):
    
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
    
    # check if any other field which is not required for the calculation of the metrics changes not triger
    # metrics calculation
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



# 3. Test fulfillment rate metrics calculations
class TestFulfillmentRateSignal(APITestCase):

    def setUp(self) -> None:
        user = User.objects.create_user('test', 'test@mail.com', 'pass123')
        self.vendor = Vendor.objects.create(
            user=user,
            name='name',
            contact_details='contact',
            address='address'
        )
        token_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data={'username':'test', 'password': 'pass123'},
            format='json'
        )
        self.access_token = token_response.data['access']
        self.data = {
            'delivery_date': timezone.now()+ timedelta(days=3),
            'items': [{'product_name': 'mobile'}, {'product_name': 'watch'}],
            'quantity': 2,
            'issue_date': timezone.now()-timedelta(days=1) 
            }
        self.reverse_name = 'purchase_order_by_id'

    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    
    # Test with empty issued purchase orders
    def test_empty_issued_purchase_order(self):

        for i in range(5):
            PurchaseOrder.objects.create(
                vendor=self.vendor,
                **self.data
            )
        
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).fulfillment_rate,
            0.0,
            'expected fulfillment rate is zero'
        )
    
    # test with completed , pending and canceled purchase orders
    def test_mixed_status_purchase_order(self):

        for i in range(5):
            purchase_order=PurchaseOrder.objects.create(
                    vendor=self.vendor,
                    **self.data
                )
            response = self.client.put(
                path= reverse(self.reverse_name, args=[purchase_order.id]),
                data={"status": "completed"},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).fulfillment_rate,
            1.0,
            'expected fulfillment rate 1.0'
        )
        
        # add pending purchase order instances

        for _ in range(5):
            PurchaseOrder.objects.create(
                vendor=self.vendor,
                **self.data
            )
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).fulfillment_rate,
            1.0,
            'expected value 1.0. value remains same eventhough pending purchase order exists'
        )

        # add canceled purchase orders

        for _ in range(5):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.put(
                path=reverse(self.reverse_name, args=[purchase_order.id]),
                data={"status": "canceled"},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        vendor = Vendor.objects.get(id=self.vendor.id)
        
        self.assertEqual(vendor.fulfillment_rate, 5/10)

# 4. Test  Metrics recalculation when a purchase order deleted.
class TestPurchaseOrderDeletePerfomanceMetricsSignal(APITestCase):

    def setUp(self) -> None:
        user = User.objects.create_user('test', 'test@mail.com', 'pass123')
        self.vendor = Vendor.objects.create(
            user=user,
            name='name',
            contact_details='contact',
            address='address'
        )
        token_response = self.client.post(path=reverse('token_obtain_pair'), data={'username':'test','password':'pass123'}, format='json')
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.access_token = token_response.data['access']
        self.reverse_name = 'purchase_order_by_id'
        self.data = {
            'delivery_date': timezone.now()+ timedelta(days=3),
            'items': [{'product_name': 'mobile'}, {'product_name': 'watch'}],
            'quantity': 2,
            'issue_date': timezone.now()-timedelta(hours=3) 
            }
        

    def tearDown(self) -> None:
        User.objects.all().delete()
        Vendor.objects.all().delete()
        PurchaseOrder.objects.all().delete()
    
    # test with one purchase order
    def test_only_one_purchase_order(self):
        purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
        #acknowledge purchase order
        response = self.client.post(
            path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
            HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(
            Vendor.objects.get(id=self.vendor.id),
            0.0,
            'value should change from zero to new value'
        )
        self.assertIsNotNone(PurchaseOrder.objects.get(id=purchase_order.id).acknowledgment_date)
        
        #change status to completed

        response = self.client.put(
            path= reverse(self.reverse_name, args=[purchase_order.id]),
            data={"status": "completed"},
            format='json',
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vendor= Vendor.objects.get(id=self.vendor.id)
        self.assertNotEqual(vendor.on_time_delivery_rate, 0.0 )
        self.assertEqual(vendor.on_time_delivery_rate, 1.0)
        self.assertEqual(vendor.fulfillment_rate, 1.0)

        # provide a quality rating

        response = self.client.put(
            path=reverse(self.reverse_name, args=[purchase_order.id]),
            data= {"quality_rating": 5.0},
            format='json',
            HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendor.objects.get(id=self.vendor.id).quality_rating_avg, 5.0)

        # delete the purchase order

        response = self.client.delete(
            path= reverse(self.reverse_name, args=[purchase_order.id]),
            HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vendor = Vendor.objects.get(id=self.vendor.id)
        # make sure all value reset to initial value
        self.assertEqual(vendor.quality_rating_avg, 0.0)
        self.assertEqual(vendor.fulfillment_rate, 0.0)
        self.assertEqual(vendor.average_response_time, 0.0)
    

    # test with multiple purchase order
    def test_multiple_purchase_order_delete(self):
        n = 5
        # add pending purchase orders
        pending_orders =[]
        for i in range(n):
            purchase_order=PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            pending_orders.append(purchase_order.id)
   
        
        # add some acknowledged only purchase orders
        acknowledged_only_orders = []
        for i in range(n):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.post(
                path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            acknowledged_only_orders.append(purchase_order.id)


        # add some ontime delivery purchase orders
        ontime_orders = []
        for i in range(n):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.post(
                path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            response = self.client.put(
                path= reverse(self.reverse_name, args=[purchase_order.id]),
                data= {"status":"completed"},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            ontime_orders.append(purchase_order.id)


        # add some over time delivery purchase orders
        overtime_orders =[]
        for i in range(n):
            purchase_order = PurchaseOrder.objects.create(
                vendor =self.vendor,
                delivery_date = timezone.now()- timedelta(days=1),
                items =[{'product_name': 'mobile'}, {'product_name': 'watch'}],
                quantity= 2,
                issue_date= timezone.now()-timedelta(hours=3)
                )
            response = self.client.post(
                path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            response = self.client.put(
                path= reverse(self.reverse_name, args=[purchase_order.id]),
                data= {"status":"completed"},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            overtime_orders.append(purchase_order.id)
            


        # add some quality rated purchase orders
        quality_rated_orders= []
        for i in range(n):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.post(
                path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            response = self.client.put(
                path= reverse(self.reverse_name, args=[purchase_order.id]),
                data= {"status":"completed", "quality_rating":4.0},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            quality_rated_orders.append(purchase_order.id)


        # add some canceled purchase orders
        canceled_orders = []
        for i in range(n):
            purchase_order = PurchaseOrder.objects.create(vendor=self.vendor, **self.data)
            response = self.client.post(
                path=reverse('acknowledge_purchase_order', args=[purchase_order.id]),
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            response = self.client.put(
                path= reverse(self.reverse_name, args=[purchase_order.id]),
                data= {"status":"canceled"},
                format='json',
                HTTP_AUTHORIZATION = f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            canceled_orders.append(purchase_order.id)
        
        #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(
            vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)
        
        m =3
        # delete some pending purchase orders
        for i in range(m):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[pending_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)

        # delete some acknowledged only purchase orders
        for _ in range(m):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[acknowledged_only_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
         #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)


        # delete some ontime delivery purchase orders
        for _ in range(m):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[ontime_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
         #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)


        # delete some overtime delivery purchase orders
        for _ in range(m):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[overtime_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
         #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)


        # delete some quality rated purchase orders
        for _ in range(m):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[quality_rated_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
         #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)



        # delete some canceled purchase orders
        for _ in range(m):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[canceled_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
         #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, (len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders))/(len(ontime_orders)+len(overtime_orders)+len(quality_rated_orders)+len(canceled_orders)))
        self.assertEqual(
            vendor.fulfillment_rate, 
            vendor.purchase_orders.filter(status='completed').count()/(vendor.purchase_orders.filter(status='completed').count()+vendor.purchase_orders.filter(status='canceled').count())
        )
        #check average response time
        self.assertAlmostEquals(vendor.average_response_time,3.0, places=1)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 4.0)


        
        # delete all purchase orders orders
        # -------------------------------------------------------#
        # delete all pending orders
        for _ in range(len(pending_orders)):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[pending_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # delete all acknowledged only orders
        for _ in range(len(acknowledged_only_orders)):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[acknowledged_only_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # delete all ontime orders
        for _ in range(len(ontime_orders)):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[ontime_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # delete all overtime orders
        for _ in range(len(overtime_orders)):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[overtime_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # delete all quality rated orders
        for _ in range(len(quality_rated_orders)):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[quality_rated_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # delete all canceled orders
        for _ in range(len(canceled_orders)):
            response = self.client.delete(
                path= reverse(self.reverse_name, args=[canceled_orders.pop()]),
                HTTP_AUTHORIZATION= f"Bearer {self.access_token}"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
         #check metrics
        vendor = Vendor.objects.get(id=self.vendor.id)
        #check fulfillment rate
        self.assertEqual(vendor.fulfillment_rate, 0.0)
        #check average response time
        self.assertEqual(vendor.average_response_time,0.0)
        #check average quality rating
        self.assertEqual(vendor.quality_rating_avg, 0.0)

        