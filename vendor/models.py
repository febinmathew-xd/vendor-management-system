from django.db import models
from django.contrib.auth.models import User
import time, random


#vendor Model

class Vendor(models.Model):
    user = models.ForeignKey(User, related_name='vendors', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=30, unique=True, blank=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
    
    def generate_vendor_code(self):
        """
        helper function to generate unique vendor code(if not provided by frontend)
        """
        timestamp = str(int(time.time() * 1000))     # current time in milliseconds to get a unique code
        random_component = random.randint(100, 999)  # to avoid conflict if vendor object created at the same time
        return f"{timestamp}{random_component}"      # combine both to get a unique vendor code
    
    def save(self, *args, **kwargs):
        if not self.vendor_code:
            self.vendor_code = self.generate_vendor_code() # if vendor code is not provided by frontend, generate a unique code
        super().save(*args, **kwargs)                      # and save the instance



#Purchase Order model

class PurchaseOrder(models.Model):

    po_number = models.CharField(max_length=40, unique=True, blank=True)
    vendor = models.ForeignKey(Vendor, related_name='purchase_orders', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    quality_rating = models.FloatField(blank=True, null=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, default=None)

    def __str__(self):
        return self.vendor.name + self.po_number
    
    def generate_po_number(self):
        """
        helper function to generate unique po number
        """
        timestamp = str(int(time.time() * 1000))     # current time in milliseconds to get a unique code
        random_component = random.randint(100, 999)  
        return f"{timestamp}{random_component}"      
    
    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self.generate_po_number() # if po number is not provided, generate a unique code
        super().save(*args, **kwargs)                      

    



