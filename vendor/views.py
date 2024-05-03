from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import UserSerializer, VendorSerializer, VendorReadOnlySerializer, PurchaseOrderSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .models import Vendor, PurchaseOrder
from django.utils import timezone
from .utils import time_difference_in_hours, find_average_response_time



class CreateUserView(generics.CreateAPIView):
    """
    create a base user. only valid user can call all other api
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]  #anyone call create user



class VendorView(APIView):

    permission_classes = [IsAuthenticated] #only authenticated user able to call this view

    def post(self, request):
        """
        create a new vendor. authentication required
        """
        
        serializer = VendorSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        list all vendor details
        """
        
        vendors = Vendor.objects.all()
        serializer = VendorReadOnlySerializer(vendors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VendorByIdView(APIView):
    
    permission_classes = [IsAuthenticated]  #only authenticated user can call this view


    def get(self, request, vendor_id):
        """
        Return a specific vendor details by id
        """
        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({"error":"invalid vendor id"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VendorReadOnlySerializer(vendor)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def put(self, request, vendor_id):
        """
        update a specific vendor details by id
        """
        
        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({"error":"invaid vendor id"}, status=status.HTTP_404_NOT_FOUND)

        if request.user != vendor.user:   #only owner can update 
            return Response({"error": "you do not have permission to update this vendor"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        serializer = VendorSerializer(vendor, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, vendor_id):
        """
        delete a vendor by its owner using vendor id
        """

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({"error":"invalid vendor id"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != vendor.user:
            return Response({"error":"you have no permission to delete this vendor"}, status=status.HTTP_403_FORBIDDEN)
        
        vendor.delete()

        return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)




class PurchaseOrderView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        serializer = PurchaseOrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):

        vendor_id = request.GET.get('vendor_id')
        

        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except Vendor.DoesNotExist:
                return Response({"error": "invalid vendor id "}, status=status.HTTP_404_NOT_FOUND)
            
            purchase_orders = vendor.purchase_orders.all()
            serializer = PurchaseOrderSerializer(purchase_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "vendor id not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        

class PurchaseOrderByIdView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, po_id):
        
        try:
            purchase_order = PurchaseOrder.objects.get(id=po_id)
            serializer = PurchaseOrderSerializer(purchase_order)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "invalid purchase order id. purchase order not found"}, status=status.HTTP_404_NOT_FOUND)
        
    
    def put(self, request, po_id):

        try:
            purchase_order = PurchaseOrder.objects.get(id=po_id)

            if purchase_order.vendor.user != request.user:
                return Response({"error": "you do not have permission to update this purchase order"}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = PurchaseOrderSerializer(purchase_order, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "purchase order id doesnot exits"}, status=status.HTTP_404_NOT_FOUND)
        

    def delete(self, request, po_id):

        try:
            purchase_order = PurchaseOrder.objects.get(id=po_id)

            if purchase_order.vendor.user != request.user:
                return Response({"error": "you do not have permission to delete this purchase order"}, status=status.HTTP_403_FORBIDDEN)
            purchase_order.delete()
            return Response({"message": "successfully deleted"}, status=status.HTTP_200_OK)
        
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "purchase order id doesnot exists"}, status=status.HTTP_404_NOT_FOUND)



class AcknowledgePurchaseOrder(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, po_id):
        
        try:
            purchase_order = PurchaseOrder.objects.get(id=po_id)
            
            if request.user != purchase_order.vendor.user:
                return Response({"error": "you do not have permission"}, status= status.HTTP_403_FORBIDDEN)
            
            purchase_order.acknowledgment_date = timezone.now()
            purchase_order.save()
            
            

            vendor = purchase_order.vendor

            # find the time taken to acknowledged by the vendor
            time_taken = time_difference_in_hours(purchase_order.acknowledgment_date, purchase_order.issue_date)
            
            # count all the acknowledged purchase orders of the vendor
            total_purchase_order = vendor.purchase_orders.filter(acknowledgment_date__isnull=False).count()
            
            # find the average response time
            # average response time is calculated after creating an acknowledged purchase order
            # so no need to worry about zero division error
            average_response_time = find_average_response_time(vendor.average_response_time,total_purchase_order, time_taken)
            
            # modify with new average and save the instance
            vendor.average_response_time = average_response_time
            vendor.save()
            
            return Response({"message": "acknowledged by the vendor"}, status=status.HTTP_200_OK)
        
        
        except PurchaseOrder.DoesNotExist:
            return Response({"error": "invalid purchase order ID, ID doesnot exists"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": "an unexpected error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorPerformanceMetricsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, vendor_id):
        
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            data = {}
            data['on_time_delivery_rate'] = vendor.on_time_delivery_rate
            data['quality_rating_avg'] = vendor.quality_rating_avg
            data['average_response_time'] = vendor.average_response_time
            data['fulfillment_rate'] = vendor.fulfillment_rate

            return Response(data, status=status.HTTP_200_OK)

        except Vendor.DoesNotExist:
            return Response({"error": "invalid vendor ID, ID not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "an unexpected error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)