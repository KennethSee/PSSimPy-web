from datetime import datetime, timedelta

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
    

def calculate_time_difference(submission_time, settlement_time, submission_day=1, settlement_day=1):
    """
    Calculate the time difference in hours between submission and settlement times, accounting for days.

    Parameters
    ----------
    submission_time : str
        Submission time in 'HH:MM' format (24-hour time).
    settlement_time : str
        Settlement time in 'HH:MM' format (24-hour time).
    submission_day : int, optional
        Day of submission (e.g., 1 for the first day). Default is 1.
    settlement_day : int, optional
        Day of settlement. Default is 1.

    Returns
    -------
    float
        Time difference in hours between submission and settlement.

    Raises
    ------
    ValueError
        If the settlement datetime is earlier than the submission datetime.

    Example
    -------
    >>> calculate_time_difference('08:00', '10:30')
    2.5
    >>> calculate_time_difference('16:00', '09:00', submission_day=1, settlement_day=2)
    17.0
    """
    # Parse submission and settlement times into datetime objects
    submission_datetime = datetime.strptime(submission_time, '%H:%M') + timedelta(days=submission_day)
    settlement_datetime = datetime.strptime(settlement_time, '%H:%M') + timedelta(days=settlement_day)

    # Check if settlement time is earlier than submission time
    if settlement_datetime < submission_datetime:
        raise ValueError("Settlement time is earlier than submission time.")

    # Calculate time difference in hours
    time_difference = (settlement_datetime - submission_datetime).total_seconds() / 3600.0

    return time_difference