def is_24_hour_format(time_str):
    try:
        # Split the string into hours and minutes
        hours, minutes = time_str.split(":")
        
        # Convert hours and minutes to integers
        hours = int(hours)
        minutes = int(minutes)
        
        # Check if hours are between 0 and 23, and minutes between 0 and 59
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return True
        return False
    except ValueError:
        # Catch if the split or conversion to int fails
        return False