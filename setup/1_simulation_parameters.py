import streamlit as st

from utils.date_time import is_24_hour_format

st.markdown("# Basic Simulation Parameters")

# Parameter fields
opening_time = st.text_input('Opening Time', value='08:00', max_chars=5, placeholder='HH:mm')
closing_time = st.text_input('Closing Time', value='17:00', max_chars=5, placeholder='HH:mm')
processing_window = st.number_input('Processing Window (minutes)', min_value=1, value=15)
num_days = st.number_input('Number of Days', min_value=1, value=1)
eod_clear_queue = st.checkbox('EOD Clear Queue')
eod_force_settlement = st.checkbox('EOD Force Settlement')

# Collapsible section for parameter definitions
with st.expander("Help?"):
    st.markdown("### Parameter Definitions")
    # Create a table with parameter definitions
    st.markdown("""
    | Parameter               | Definition                                                                 |
    |-------------------------|-----------------------------------------------------------------------------|
    | **Opening Time**         | The opening time for each simulation day, formatted as HH:MM.                |
    | **Closing Time**         | The closing time for each simulation day, formatted as HH:MM.                |
    | **Processing Window**    | Duration in minutes of each processing window within a simulation day.       |
    | **Number of Days**       | The number of days the simulation will run for.                              |
    | **EOD Clear Queue**      | Option to cancel all transactions still in queue at EOD.                     |
    | **EOD Force Settlement** | Option to force all outstanding transactions inside and outside queue to settle at EOD.    |
    """)

if st.button('Set Parameters'):
    # validate data
    validation_fail = False
    if not is_24_hour_format(opening_time):
        validation_fail = True
        st.error('Opening Time is not in the correct format.')
    if not is_24_hour_format(closing_time):
        validation_fail = True
        st.error('Closing Time is not in the correct format.')
    
    if not validation_fail:
        st.session_state['Parameters'] = {
            'Opening Time': opening_time,
            'Closing Time': closing_time,
            'Processing Window': processing_window,
            'Number of Days': num_days,
            'EOD Clear Queue': eod_clear_queue,
            'EOD Force Settlement': eod_force_settlement
        }
        st.success('Parameters successfully set.')
