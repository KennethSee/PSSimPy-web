import streamlit as st
from PSSimPy.credit_facilities import AbstractCreditFacility

st.write('# Customize Credit Facility Agent')

# Fee Calculation

# Lending Condition
# This should determine the conditions required to lend the credit in full or partial. The final amount of credit lent should be added to the account balance.

# Collection Logic
# It should be implemented such that for a given account, the amount of total credit and total fee is reduced. No return is expected.