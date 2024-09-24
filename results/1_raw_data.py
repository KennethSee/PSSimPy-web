import streamlit as st

st.markdown("# Raw Data Output")

if st.session_state['Random Transactions']:
    st.markdown('## Transactions Arrival')
    st.dataframe(st.session_state['Log Files']['Transactions Arrival'])

st.markdown('## Processed Transactions')
st.dataframe(st.session_state['Log Files']['Processed Transactions'])

st.markdown('## Account Balances')
st.dataframe(st.session_state['Log Files']['Account Balance'])

st.markdown('## Queue Statistics')
st.dataframe(st.session_state['Log Files']['Queue Stats'])

st.markdown('## Credit Facility Statistics')
st.dataframe(st.session_state['Log Files']['Credit Facility'])

st.markdown('## Transaction Fees')
st.dataframe(st.session_state['Log Files']['Transaction Fees'])