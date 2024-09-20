import streamlit as st
import plotly.express as px
from PSSimPy.simulator import ABMSim

st.markdown("# Preview")

# Section 1: Basic Parameters
st.markdown("## Basic Parameters")

# Use columns to arrange parameters in two columns
col1, col2 = st.columns(2)

# First column for first half of the parameters
with col1:
    st.markdown(f"**Opening Time:** {st.session_state['Parameters']['Opening Time']}")
    st.markdown(f"**Closing Time:** {st.session_state['Parameters']['Closing Time']}")
    st.markdown(f"**Processing Window:** {st.session_state['Parameters']['Processing Window']} minutes")

# Second column for second half of the parameters
with col2:
    st.markdown(f"**Number of Days:** {st.session_state['Parameters']['Number of Days']}")
    st.markdown(f"**EOD Clear Queue:** {st.session_state['Parameters']['EOD Clear Queue']}")
    st.markdown(f"**EOD Force Settlement:** {st.session_state['Parameters']['EOD Force Settlement']}")

st.divider()

# Section 2: Banks and Accounts
st.markdown("## Banks and Accounts")

# Create a hierarchical sunburst chart for banks and accounts
df_banks = st.session_state['Input Data']['Banks']
if 'strategy_type' not in df_banks.columns:
    # default strategy type to "Normal" if no strategy specified
    df_banks['strategy_type'] = 'Normal'
df_accounts = st.session_state['Input Data']['Accounts'].merge(df_banks, left_on='owner', right_on='name')
df_sunburst = df_accounts.copy()
df_sunburst['level_0'] = 'Banks'

fig = px.sunburst(df_sunburst, 
                  path=['level_0', 'strategy_type', 'owner', 'id'], 
                  title='Bank-Account Hierarchy with Strategies',
                  color='strategy_type',  # Color by strategy type for clear differentiation
                  color_discrete_sequence=px.colors.qualitative.Set3
                  )
st.plotly_chart(fig)

st.divider()

if st.button('Begin Simulation'):
    with st.spinner('Running simulation...'):
        # identify params
        sim_params = {
            'name': 'PSSimPy-web',
            'banks': st.session_state['Input Data']['Banks'], 
            'accounts': st.session_state['Input Data']['Accounts'],
            'open_time': st.session_state['Parameters']['Opening Time'],
            'close_time': st.session_state['Parameters']['Closing Time'],
            'processing_window': st.session_state['Parameters']['Processing Window'],
            'num_days': st.session_state['Parameters']['Number of Days'],
            'eod_clear_queue': st.session_state['Parameters']['EOD Clear Queue'],
            'eod_force_settlement': st.session_state['Parameters']['EOD Force Settlement']
        }
        if st.session_state['Random Transactions']:
            sim_params['txn_arrival_prob'] = st.session_state['Transaction Probability']
            sim_params['txn_amount_range'] = st.session_state['Transaction Amount Range']
        else:
            sim_params['transactions'] = st.session_state['Input Data']['Transactions']

        # initialize and run simulator
        sim = ABMSim(**sim_params)
        sim.run()

    st.success('Simulation completed!')
