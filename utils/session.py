import streamlit as st
import pandas as pd
from PSSimPy.constraint_handler import PassThroughHandler
from PSSimPy.transaction_fee import FixedTransactionFee

from utils.helper import initialize_dict_key

def initialize_session_state_variables():
    # Parameters
    initialize_dict_key(st.session_state, 'Parameters', {
            'Opening Time': None,
            'Closing Time': None,
            'Processing Window': None,
            'Number of Days': None,
            'EOD Clear Queue': None,
            'EOD Force Settlement': None
    })
    # Input Data
    initialize_dict_key(st.session_state, 'Input Data', {
            'Banks': pd.DataFrame(columns=['name']),
            'Accounts': pd.DataFrame(columns=['id', 'owner', 'balance']),
            'Transactions': None
    })
    # Random Transactions
    initialize_dict_key(st.session_state, 'Random Transactions', False)
    # Transaction Probability
    initialize_dict_key(st.session_state, 'Transaction Probability', None)
    # Transaction Amount Range
    initialize_dict_key(st.session_state, 'Transaction Amount Range', None)
    # Bank Strategies
    initialize_dict_key(st.session_state, 'Bank Strategies', {})
    # Constraint Handler
    initialize_dict_key(st.session_state, 'Constraint Handler', (PassThroughHandler, None)) # default to pass through
    # Transaction Fee
    initialize_dict_key(st.session_state, 'Transaction Fee', {
        'rate': None,
        'class': FixedTransactionFee, # placeholder
        'implementation': None
    })