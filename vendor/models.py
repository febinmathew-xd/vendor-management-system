from django.db import models
from django.contrib.auth.models import User
import time, random


# vendor Model
# This model stores essential information about each vendor and their performance metrics.
class Vendor(models.Model):
    user = models.ForeignKey(User, related_name='vendors', on_delete=models.CASCADE) # link to the User model
    name = models.CharField(max_length=100)  # name of the vendor
    contact_details = models.TextField()     # contact informantion of the vendor
    address = models.TextField()             # physical address of the vendor
    vendor_code = models.CharField(max_length=30, unique=True, blank=True) # a unique ID for the vendor
    on_time_delivery_rate = models.FloatField(default=0.0)  # tracks the percentage of on-time delivery
    quality_rating_avg = models.FloatField(default=0.0)     # Average rating of quality based on purchase orders
    average_response_time = models.FloatField(default=0.0)  # Average time taken to acknowledge purchase orders (calculated in hours)
    fulfillment_rate = models.FloatField(default=0.0)       # Percentage of purchase orders fulfilled successfully
    
    # string representation
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



# Purchase Order model
# This model captures the details of each purchase order and is used to calculate various
# performance metrics.
class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=40, unique=True, blank=True)  # unique number identifying the purchse order
    vendor = models.ForeignKey(Vendor, related_name='purchase_orders', on_delete=models.CASCADE)  # link to the vendor model
    order_date = models.DateTimeField(auto_now_add=True)   # date when the order was placed
    delivery_date = models.DateTimeField()  # expected or actual delivery date of the order
    items = models.JSONField()              # details of items ordered
    quantity = models.IntegerField()        # total quantity of items in the purchase order
    status = models.CharField(max_length=20, default='pending')  # current status of the purchase order (e.g., pending, completed, canceled)
    quality_rating = models.FloatField(blank=True, null=True)    # rating given to the vendor for this purchase order (nullable)
    issue_date = models.DateTimeField()                          # timestamp when the purchase order was issued to the vendor
    acknowledgment_date = models.DateTimeField(null=True, default=None)  # Timestamp when the vendor acknowledged the purchase order (nullable)
    
    # string representation
    def __str__(self):
        return self.vendor.name + self.po_number
    
    class Meta:
        ordering = ['-order_date'] # descending order by order date
    
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

    

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, related_name='historical_performances', on_delete=models.CASCADE)  # link to the Vendor model
    date = models.DateTimeField(auto_now_add=True)    # date of the performance record
    on_time_delivery_date = models.FloatField()       # historical record of the on-time delivery rate
    quality_rating_avg = models.FloatField()          # historical record of the quality rating average
    average_response_time = models.FloatField()       # historical record of the average response time
    fulfillment_rate = models.FloatField()            # historical record of the fulfilment rate

    # string representation
    def __str__(self) -> str:
        return self.vendor.name+str(self.date)
    
    class Meta:
        ordering = ['-date'] # descending order by date

