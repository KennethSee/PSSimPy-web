import os
import streamlit as st
import plotly.express as px
from PSSimPy.simulator import ABMSim
from PSSimPy.constraint_handler import AbstractConstraintHandler

from utils.file import log_file_reader, delete_log_files
from utils.session import save_simulation_settings

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

# Section 3: Show non-bank agents that have been implemented
st.markdown("## Agents Implemented")
# Initialize the agent implementation states
agents = {
    "Settlement Agent": st.session_state['Constraint Handler']['implementation'] is not None 
                        or st.session_state['Transaction Fee']['implementation'] is not None,
    "Queue Agent": st.session_state['Queue']['implementation'] is not None,
    "Credit Facility Agent": st.session_state['Credit Facility']['implementation'] is not None,
}

# Helper function to display ticks and crosses
def display_status(is_implemented):
    return "✅" if is_implemented else "❌"

# Display the agents and their statuses in a row
columns = st.columns(len(agents))
for col, (agent_name, implemented) in zip(columns, agents.items()):
    col.markdown(f"**{agent_name}**")
    col.markdown(display_status(implemented))

if not agents['Settlement Agent']:
    st.warning('Settlement Agent is not implemented. It will default to no constraints and no transaction fees.')
if not agents['Queue Agent']:
    st.warning('Queue Agent is not implemented. It will default to a pass-through queue.')
if not agents['Credit Facility Agent']:
    st.warning('Credit Facility Agent is not implemented. It will default to a simple priced credit facility.')

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
            'eod_force_settlement': st.session_state['Parameters']['EOD Force Settlement'],
            'constraint_handler': st.session_state['Constraint Handler']['class'](),
            'credit_facility': st.session_state['Credit Facility']['class'](),
            'transaction_fee_handler': st.session_state['Transaction Fee']['class'](),
            'transaction_fee_rate': st.session_state['Transaction Fee']['rate'],
            'strategy_mapping': {key: val['class'] for (key, val) in st.session_state['Bank Strategies'].items()}
        }

        if st.session_state['Random Transactions']:
            sim_params['txn_arrival_prob'] = st.session_state['Transaction Probability']
            sim_params['txn_amount_range'] = st.session_state['Transaction Amount Range']
        else:
            sim_params['transactions'] = st.session_state['Input Data']['Transactions']

        # initialize and run simulator
        sim = ABMSim(**sim_params)
        sim.run()

        # ingest simulation output
        st.session_state['Log Files'] = {
            'Processed Transactions': log_file_reader('processed_transactions'),
            'Transaction Fees': log_file_reader('transaction_fees'),
            'Queue Stats': log_file_reader('queue_stats'),
            'Account Balance': log_file_reader('account_balance'),
            'Credit Facility': log_file_reader('credit_facility')
        }
        if st.session_state['Random Transactions']:
            st.session_state['Log Files']['Transactions Arrival'] = log_file_reader('transactions_arrival')

        # clear log files from directory
        delete_log_files()

    st.success('Simulation completed!')

st.write('# Export Simulation Settings')
# Save simulation settings
SAVE_PATH = "./saved_settings"
os.makedirs(SAVE_PATH, exist_ok=True)
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    # Text input for simulation setting name
    setting_name = st.text_input("Setting Name", placeholder="Enter setting name")
with col2:
    # Checkbox for export option
    export_data = st.checkbox("Export data?")
with col3:
    # Button to save simulation settings
    if st.button("Export Simulation Settings"):
        # Check if a .zip file with the same name already exists
        zip_path = os.path.join(SAVE_PATH, f"{setting_name}.zip")
        if os.path.exists(zip_path):
            # If the file exists, show an error message
            st.error(f"A settings file named '{setting_name}.zip' already exists. Please use a different name.")
        elif setting_name.strip() == "":
            # Handle case where setting name is empty
            st.error("The setting name cannot be empty. Please enter a valid name.")
        else:
            # If no conflict, call the save function
            save_simulation_settings(setting_name, export_data)
            st.success(f"'{setting_name}' has been successfully exported.")