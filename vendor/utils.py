

def time_difference_in_hours(current_time, prev_time):
    """
    calculate time difference between two time stamps and return the difference in hours
    type:current_time : timestamp
    type:prev_time : timestamp
    rtype: float

    """

    difference = current_time - prev_time
    total_seconds = difference.total_seconds()
    hours = total_seconds/3600
    
    return round(hours, 2)


def find_average_response_time(current_avg, total_po, value ):
    """
    find the average response time by calculating with current average, total no of responses and the new value
    applies average = total/number formula to calculate new average response time
    """
    if total_po == 0: return 0.0
    
    total = current_avg*(total_po -1)
    new_total = total + value
    new_average = new_total/total_po

    return round(new_average, 2)

def find_quality_rating_average(current_avg_rating, total_rating, value, fresh=True, prev_rating=None):

    """
    find quality average rating by using current average , total rating count and new value.
    mathematical formula average = total/number is appiled here.
    fresh is true means value is new and if it false we need to calculate average by replacing old value to new value,
    so, previous rating value is required if fresh is false
    """
    total_average = current_avg_rating*total_rating
    if fresh == True:
        new_average_rating = (total_average + value)/(total_rating+1)
        return round(new_average_rating, 2)
    if not fresh and not prev_rating:
        raise ValueError("previous ratings should provide of value is not fresh")
    new_average_rating = (total_average-prev_rating+ value)/ total_rating
    return round(new_average_rating, 2)


# def on_time_delivery_rate(current_rate, total, value):
#     total_delivery = current_rate*total
#     new_rate = (total_delivery+value)/(total+1)
#     return round(new_rate,3)