from utils.date_time import calculate_time_difference

def turnover_ratio(total_payments_settled: float, average_liquidity: float) -> float:
    """
    The Turnover Ratio is a key metric used to assess the efficiency of liquidity usage in a payment system.
    It is calculated using the formula:

        Turnover Ratio = Total Gross Value of Payments Settled / Average Intraday Liquidity

    Parameters
    ----------
    total_payments_settled : float
        The total gross value of all payments settled over the period of analysis.
    average_liquidity : float
        The average amount of liquidity available to participants during the same period.

    Returns
    -------
    float
        The calculated Turnover Ratio.
    """
    if average_liquidity == 0:
        raise ValueError("Average liquidity must be greater than zero.")
    return total_payments_settled/average_liquidity


def average_payment_delay(submission_times, settlement_times, submission_days=None, settlement_days=None, amounts=None, weighted=False):
    """
    Calculate the Average Payment Delay in a Large Value Payment System (LVPS).

    This function calculates the average delay between the submission and settlement of payments.
    It handles times provided in 'HH:MM' format and optional day parameters.

    Parameters
    ----------
    submission_times : list of str
        List of submission times in 'HH:MM' format (24-hour time).
    settlement_times : list of str
        List of settlement times in 'HH:MM' format (24-hour time).
    submission_days : list of int, optional
        List of days corresponding to each submission time. Default assumes all times are on the same day.
    settlement_days : list of int, optional
        List of days corresponding to each settlement time. Default assumes all times are on the same day.
    amounts : list of floats, optional
        List of amounts corresponding to each payment. Default is None.
    weighted : bool, optional
        If True, calculate a weighted average delay based on the payment amounts.

    Returns
    -------
    float
        The (weighted) average payment delay in minutes. Returns 0.0 if total weight is zero.

    Raises
    ------
    ValueError
        If the lengths of input lists do not match.
        If any settlement time is earlier than the corresponding submission time.
    """
    N = len(submission_times)
    if N != len(settlement_times):
        raise ValueError("The number of submission times must match the number of settlement times.")

    # If days are not provided, assume all times are on the same day (day 0)
    if submission_days is None:
        submission_days = [0] * N
    if settlement_days is None:
        settlement_days = [0] * N

    if len(submission_days) != N or len(settlement_days) != N:
        raise ValueError("The number of submission days and settlement days must match the number of payments.")

    # If weighted, amounts should be provided and match the number of payments
    if weighted:
        if amounts is None:
            raise ValueError("Amounts must be provided for weighted average calculation.")
        if len(amounts) != N:
            raise ValueError("The number of amounts must match the number of payments.")
    
    total_delay = 0.0
    total_weight = 0.0 if weighted else N

    for i in range(N):
        # Calculate the delay in minutes
        delay_in_minutes = calculate_time_difference(
            submission_time=submission_times[i],
            settlement_time=settlement_times[i],
            submission_day=submission_days[i],
            settlement_day=settlement_days[i]
        )
        
        if weighted:
            total_delay += delay_in_minutes * amounts[i]
            total_weight += amounts[i]
        else:
            total_delay += delay_in_minutes

    # Safely calculate the average delay, returning 0.0 if total_weight is zero
    average_delay = total_delay / total_weight if total_weight != 0 else 0.0
    return average_delay
