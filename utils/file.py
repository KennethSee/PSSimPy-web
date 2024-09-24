import os
import pandas as pd

def check_missing_headers(df, required_headers: list):
    return [col for col in required_headers if col not in df.columns]


def log_file_reader(log_file_type: str):
    """
    Reads and returns log files as a Pandas dataframe. Valid log file types are:
    1. account_balance
    2. credit_facility
    3. queue_stats
    4. transaction_fees
    5. transactions_arrival
    6. processed_transactions
    
    Raises:
        ValueError: If the log_file_type is invalid.
    """
    # List of valid log file types
    valid_log_file_types = [
        "account_balance",
        "credit_facility",
        "queue_stats",
        "transaction_fees",
        "transactions_arrival",
        "processed_transactions"
    ]
    
    # Check if the provided log_file_type is valid
    if log_file_type not in valid_log_file_types:
        raise ValueError(f"Invalid log file type: {log_file_type}. Valid types are: {', '.join(valid_log_file_types)}")

    # Read and return the log file as a Pandas DataFrame
    df = pd.read_csv(f'PSSimPy-web-{log_file_type}.csv')
    return df

def delete_log_files():
    files_to_remove = [
        "PSSimPy-web-account_balance.csv",
        "PSSimPy-web-credit_facility.csv",
        "PSSimPy-web-processed_transactions.csv",
        "PSSimPy-web-queue_stats.csv",
        "PSSimPy-web-transaction_fees.csv",
        "PSSimPy-web-transactions_arrival.csv"
    ]
    for filename in files_to_remove:
        file_path = os.path.join(filename)  # Create the full file path
        if os.path.exists(file_path):  # Check if the file exists
            os.remove(file_path)  # Remove the file
            print(f"Removed {filename}")  # Confirm removal