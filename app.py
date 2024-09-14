import streamlit as st

# define pages
landing_page = st.Page("landing.py", title="Hello", icon="👋")
setup_parameters_page = st.Page("setup/1_simulation_parameters.py", 
                                title="Simulation Parameters", 
                                icon=":material/settings:")
setup_input_page = st.Page("setup/2_input_data.py",
                           title="Input Data",
                           icon=":material/input:")
setup_preview_page = st.Page("setup/3_preview.py",
                             title="Preview",
                             icon=":material/preview:")
results_raw_page = st.Page("results/1_raw_data.py",
                           title="Raw Data",
                           icon=":material/dataset:")
results_liquidity_page = st.Page("results/2_liquidity.py",
                                 title="Liquidity",
                                 icon=":material/water_drop:")

pg = st.navigation(
    {
        "Landing": [landing_page],
        "Setup": [setup_parameters_page, setup_input_page, setup_preview_page],
        "Reulsts": [results_raw_page, results_liquidity_page]
    }
)
st.set_page_config(
    page_title="Large Value Payment System Simulator",
    page_icon="👋",
)

pg.run()
