import streamlit as st

from utils.session import initialize_session_state_variables

# define pages
landing_page = st.Page("landing.py", title="Hello", icon="👋")
setup_parameters_page = st.Page("setup/1_simulation_parameters.py", 
                                title="Simulation Parameters", 
                                icon=":material/settings:")
setup_input_page = st.Page("setup/2_input_data.py",
                           title="Input Data",
                           icon=":material/input:")
setup_customize_agents_page = st.Page("setup/3_customize_bank_agents.py",
                           title="Customize Bank Agents",
                           icon=":material/account_balance:")
setup_customize_settlement_agent_page = st.Page("setup/4_customize_settlement_agent.py",
                             title="Customize Settlement Agent",
                             icon=":material/sync_alt:")
setup_customize_queue_page = st.Page("setup/5_customize_queue_agent.py",
                             title="Customize Queue Agent",
                             icon=":material/table_rows:")
setup_customize_credit_facility_page = st.Page("setup/6_customize_credit_facility_agent.py",
                             title="Customize Credit Facility Agent",
                             icon=":material/currency_exchange:")
setup_preview_page = st.Page("setup/7_preview.py",
                             title="Preview",
                             icon=":material/preview:")
results_raw_page = st.Page("results/1_raw_data.py",
                           title="Raw Data",
                           icon=":material/dataset:")
results_liquidity_page = st.Page("results/2_liquidity.py",
                                 title="Liquidity",
                                 icon=":material/water_drop:")
results_credit_usage_page = st.Page("results/3_credit_usage.py",
                                    title="Credit Usage",
                                    icon=":material/credit_card:")

pg = st.navigation(
    {
        "Landing": [landing_page],
        "Setup": [setup_parameters_page, setup_input_page, setup_customize_agents_page, setup_customize_settlement_agent_page, setup_customize_queue_page, setup_customize_credit_facility_page, setup_preview_page],
        "Results": [results_raw_page, results_liquidity_page, results_credit_usage_page]
    }
)
st.set_page_config(
    page_title="Large Value Payment System Simulator",
    page_icon="👋",
)

pg.run()
initialize_session_state_variables()
