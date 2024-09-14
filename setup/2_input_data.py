import streamlit as st
import pandas as pd

from utils.file_validation import check_missing_headers

st.markdown("# Input Data")

# Manage session state for the checkbox to avoid unwanted persistence
if 'random_transactions_flag' not in st.session_state:
    st.session_state['random_transactions_flag'] = False

st.markdown("## Banks")
df_banks = None
uploaded_banks = st.file_uploader("Upload your Banks input file", type=["csv"])
if uploaded_banks is not None:
    df_banks = pd.read_csv(uploaded_banks)

    # validation
    bank_upload_validation_fail = False
    missing_bank_headers = check_missing_headers(df_banks, ['name'])
    if len(missing_bank_headers) > 0:
        bank_upload_validation_fail = True
        st.error(f"The following required column(s) are missing: {', '.join(missing_bank_headers)}")

    if not bank_upload_validation_fail:
        st.dataframe(df_banks)
    else:
        df_banks = None

st.markdown("## Accounts")
df_accounts = None
uploaded_accounts = st.file_uploader("Upload your Accounts input file", type=["csv"])
if uploaded_accounts is not None:
    df_accounts = pd.read_csv(uploaded_accounts)

    # validation
    account_upload_validation_fail = False
    missing_account_headers = check_missing_headers(df_accounts, ['id', 'owner', 'balance'])
    if len(missing_account_headers) > 0:
        account_upload_validation_fail = True
        st.error(f"The following required column(s) are missing: {', '.join(missing_account_headers)}")

    if not account_upload_validation_fail:
        st.dataframe(df_accounts)
    else:
        df_accounts = None

st.markdown("## Transactions")
df_transactions = None
st.session_state['random_transactions_flag'] = st.checkbox("Random system-generated transactions?")
if st.session_state['random_transactions_flag']:
    txn_arrival_prob = st.number_input('Transaction Arrival Probability', min_value=0.00, max_value=1.00, step=0.01, value=0.5)
    min_txn_amount = st.number_input('Minimum Transaction Amount', min_value=1, value=1)
    max_txn_amount = st.number_input('Maximum Transaction Amount', min_value=1, value=100)
else:
    uploaded_transactions = st.file_uploader("Upload your Transactions input file", type=["csv"])
    if uploaded_transactions is not None:
        df_transactions = pd.read_csv(uploaded_transactions)

        # validation
        transaction_upload_validation_fail = False
        missing_transaction_headers = check_missing_headers(df_transactions, ['sender_account', 'recipient_account', 'amount', 'time'])
        if len(missing_transaction_headers) > 0:
            transaction_upload_validation_fail = True
            st.error(f"The following required column(s) are missing: {', '.join(missing_transaction_headers)}")

        if not transaction_upload_validation_fail:
            st.dataframe(df_transactions)
        else:
            df_transactions = None

if st.button('Register Input Data'):
    # validation
    register_fail = False
    if df_banks is None:
        register_fail = True
        st.error('Please upload Banks data.')
    if df_accounts is None:
        register_fail = True
        st.error('Please upload Accounts data.')
    if not st.session_state['random_transactions_flag']:
        if df_transactions is None:
            register_fail = True
            st.error('Please upload Transactions data.')
    
    if not register_fail:
        st.session_state['Input Data'] = {'Banks': df_banks, 'Accounts': df_accounts}
        if st.session_state['random_transactions_flag']:
            st.session_state['Random Transactions'] = True
        else:
            st.session_state['Random Transactions'] = False
            st.session_state['Input Data']['Transactions'] = df_transactions
        st.success('Input Data successfully registered!')
