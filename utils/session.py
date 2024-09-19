import streamlit as st

from utils.helper import initialize_dict_key

def initialize_session_state_variables():
    # Parameters
    initialize_dict_key(st.session_state, 'Parameters', {})
    # Input Data
    initialize_dict_key(st.session_state, 'Input Data', {})
    # Random Transactions
    initialize_dict_key(st.session_state, 'Random Transactions', False)
    # Transaction Probability
    initialize_dict_key(st.session_state, 'Transaction Probability', None)
    # Transaction Amount Range
    initialize_dict_key(st.session_state, 'Transaction Amount Range', None)
    # Bank Strategies
    initialize_dict_key(st.session_state, 'Bank Strategies', {})