from django.db.models.signals import  pre_save, post_delete
from django.dispatch import receiver
from .models import PurchaseOrder
from .utils import find_quality_rating_average, time_difference_in_hours
from django.utils import timezone
from django.db import transaction


# calculate vendor metrics when the values of the purchase order changes.(necessary for metrics calculation)
# efficienlty calculate quality rating average, on time delivery rate and fulfillment rate of the respected vendor in realtime
@receiver(pre_save, sender=PurchaseOrder)
def purchase_order_signals(sender, instance, **kwargs):
    with transaction.atomic():
        try:
            prev = sender.objects.get(id=instance.id)

            # calculate quality rating average when a quality rating is provided to purchase order
            # calculate only if a quaity rating is provided even if the purchase order is delivered or canceled
            if prev.quality_rating != instance.quality_rating:
                vendor = instance.vendor
                total_ratings= vendor.purchase_orders.exclude(quality_rating=None).count()
                previous_average_rating = vendor.quality_rating_avg

                # calculate and update quality rating average if the quality rating is newly provided
                if prev.quality_rating is None:
                    vendor.quality_rating_avg = find_quality_rating_average(previous_average_rating, total_ratings, instance.quality_rating)
                    vendor.save()
            
                # re-calculate and update quality rating average if modified existing rating
                # do not consider it as a new value, so the total ratings count remains same
                else:
                    vendor.quality_rating_avg = find_quality_rating_average(
                        previous_average_rating, 
                        total_ratings, 
                        instance.quality_rating, 
                        fresh=False, 
                        prev_rating=prev.quality_rating)
                    vendor.save()

            # calculate ontime delivery rate when the purchase order status changed to completed
            if prev.status != instance.status and instance.status == 'completed':
            
                vendor = instance.vendor
                count = 1 if timezone.now() <= instance.delivery_date else 0  # check it is a ontime delivery or not
                total_ontime_delivered_orders = vendor.purchase_orders.filter(status='completed', delivery_date__gte=timezone.now()).count() + count
                total_delivered_orders = vendor.purchase_orders.filter(status='completed').count() +1
                vendor.on_time_delivery_rate = round(total_ontime_delivered_orders/total_delivered_orders, 3)
                vendor.save()

            # calculate fulfillment rate when the purchase order status changed to completed/ canceled
            if prev.status != instance.status and (instance.status=='completed' or instance.status=='canceled'):
                vendor = instance.vendor
                if instance.status =='completed':
                    total_completed = vendor.purchase_orders.filter(status='completed').count()+1
                    total_canceled = vendor.purchase_orders.filter(status='canceled').count()
                if instance.status =='canceled':
                    total_completed = vendor.purchase_orders.filter(status='completed').count()
                    total_canceled = vendor.purchase_orders.filter(status='canceled').count() +1
                    
                if total_completed+ total_canceled == 0:  # avoid zero division error
                    fulfillment_rate = 0.0
                else:
                    fulfillment_rate = round(total_completed/(total_completed+total_canceled), 2) # calculate fulfillment rate
                    
                vendor.fulfillment_rate = fulfillment_rate
                vendor.save()



        except PurchaseOrder.DoesNotExist:
            pass

# recalculate and update vendor metrics when a purchase order deleted
# if any of the purchase order which involved in the matrics calculation gets deleted, recalculate
# the metrics realtime. avoids inaccuracy by handling this edge case

@receiver(post_delete, sender=PurchaseOrder)
def delete_purchase_order_signals(sender, instance, **kwargs):

    # recalculate quality rating
    # recalculate only if the deleted purchase order has quality rating. because if the quality rating is None,
    # this purchase order is not part of the metrics calculated..so we can delete it safely with out modifying anything
    if instance.quality_rating is not None:
        vendor = instance.vendor
        current_quality_rating_avg = vendor.quality_rating_avg
        rating_count = vendor.purchase_orders.exclude(quality_rating=None).count()
        previous_rating_count = rating_count +1 # because current instance is deleted
        rating_avg_sum = current_quality_rating_avg * previous_rating_count # average = totalsum/total number
        if rating_count ==0:
            new_average = 0.0
        else:
            new_average = (rating_avg_sum - instance.quality_rating)/rating_count
        vendor.quality_rating_avg = new_average
        vendor.save()


    # recalculate fulfillment rate

    if instance.status != 'pending':
        vendor = instance.vendor
        completed_orders = vendor.purchase_orders.filter(status='completed').count()
        canceled_orders = vendor.purchase_orders.filter(status='canceled').count()
        total_orders = completed_orders+ canceled_orders
        if total_orders ==0:
            fulfillment_rate = 0.0
        else:
            fulfillment_rate = completed_orders/total_orders
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()



    # recalculate average response time when an acknowledged purchase order gets deleted
    if instance.acknowledgment_date is not None:
        vendor = instance.vendor
        time_taken = time_difference_in_hours(instance.acknowledgment_date, instance.issue_date)
        order_count = vendor.purchase_orders.exclude(acknowledgment_date=None).count()
        if order_count ==0:
            average_response_time = 0.0
        else:
            previous_average_response_time = vendor.average_response_time
            previous_order_count = order_count+1

            total_response_time = previous_average_response_time*previous_order_count
            average_response_time = (total_response_time- time_taken)/order_count
        
        vendor.average_response_time = average_response_time
        vendor.save()

    