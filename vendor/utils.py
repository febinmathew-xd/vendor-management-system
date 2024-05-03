

def time_difference_in_hours(current_time, prev_time):

    difference = current_time - prev_time
    total_seconds = difference.total_seconds()
    hours = total_seconds/3600
    
    return round(hours, 2)


def find_average_response_time(current_avg, total_po, value ):

    if total_po == 0: return 0.0
    
    total = current_avg*(total_po -1)
    new_total = total + value
    new_average = new_total/total_po

    return round(new_average, 2)