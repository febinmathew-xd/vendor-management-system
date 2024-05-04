from django.db.models.signals import  pre_save
from django.dispatch import receiver
from .models import PurchaseOrder
from .utils import find_quality_rating_average
from django.utils import timezone
from django.db import transaction

@receiver(pre_save, sender=PurchaseOrder)
def purchase_order_signals(sender, instance, **kwargs):
    with transaction.atomic():
        try:
            prev = sender.objects.get(id=instance.id)

            # calculate quality rating average when a quality rating is provided to each purchase order
            if prev.quality_rating != instance.quality_rating:
                vendor = instance.vendor
                total_ratings= vendor.purchase_orders.exclude(quality_rating=None).count()
                previous_average_rating = vendor.quality_rating_avg

                # calculate and update quality rating average if the quality rating is newly provided
                if prev.quality_rating is None:
                    vendor.quality_rating_avg = find_quality_rating_average(previous_average_rating, total_ratings, instance.quality_rating)
                    vendor.save()
            
                # re-calculate and update quality rating average if modified existing rating
                else:
                    vendor.quality_rating_avg = find_quality_rating_average(
                        previous_average_rating, 
                        total_ratings, 
                        instance.quality_rating, 
                        fresh=False, 
                        prev_rating=prev.quality_rating)
                    vendor.save()

            # calculate ontime delivery rate
            if prev.status != instance.status and instance.status == 'completed':
            
                vendor = instance.vendor
                count = 1 if timezone.now() <= instance.delivery_date else 0
                total_ontime_delivered_orders = vendor.purchase_orders.filter(status='completed', delivery_date__gte=timezone.now()).count() + count
                total_delivered_orders = vendor.purchase_orders.filter(status='completed').count() +1
                vendor.on_time_delivery_rate = round(total_ontime_delivered_orders/total_delivered_orders, 3)
                vendor.save()

                # calculate fulfillment rate
        
            if prev.status != instance.status and (instance.status=='completed' or instance.status=='canceled'):
                vendor = instance.vendor
                total_completed = vendor.purchase_orders.filter(status='completed').count()
                total_canceled = vendor.purchase_orders.filter(status='canceled').count()
                if total_completed+ total_canceled == 0:  # avoid zero division error
                    fulfillment_rate = 0.0
                else:
                    fulfillment_rate = round(total_completed/(total_completed+total_canceled), 3)
                vendor.fulfillment_rate = fulfillment_rate
                vendor.save()



        except PurchaseOrder.DoesNotExist:
            pass
    