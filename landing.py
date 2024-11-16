import streamlit as st
from utils.session import import_simulation_setting

st.write('''
         # Welcome to PSSimPy: A Large-Value Payment System Simulator

        This web application leverages the **PSSimPy** Python library (version 0.1.4) to provide a powerful and flexible simulation tool for modeling and analyzing Large-Value Payment Systems (LVPS). PSSimPy supports advanced agent-based modeling, allowing users to explore complex payment system dynamics, including potential blockchain-based designs. For more information about PSSimPy, visit the [library documentation and source code](https://github.com/KennethSee/PSSimPy).

        ## Features and Workflow

        ### 1. Setup
        Configure LVPS scenarios and agent behaviors via dedicated pages in the "Setup" section. Pre-built templates are available for ease of use, while advanced users can implement custom functionalities by writing their own Python code.

        ### 2. Preview and Run Simulations
        The "Preview" page allows you to review your simulation settings and run the simulation. You can export your customized settings and implementation as a `.zip` file, saved in a `saved_settings` folder in your local directory. This export can be re-imported using the file upload functionality below.

        ### 3. Analyze Results
        The "Results" section provides access to raw simulation outputs and interactive visualizations of key metrics, such as liquidity usage and payment delays, to support decision-making.

        ---

        This simulator is designed to support researchers, policymakers, and financial institutions in understanding LVPS dynamics and evaluating the impact of design choices, including those involving blockchain technology. Whether you are analyzing existing systems or testing innovative designs, PSSimPy offers the tools you need to explore and assess LVPS performance comprehensively.

         ''')

st.write('## Import Simulation Setting')

# Add a file uploader for importing simulation settings
uploaded_file = st.file_uploader(
    "Import Simulation Setting (.zip)", 
    type="zip", 
    help="Upload a .zip file containing the simulation setting."
)

# Add an "Import" button to trigger the import logic
if st.button("Import Simulation Setting"):
    if uploaded_file is not None:
        st.success('Settings successfully imported!')
        import_simulation_setting(uploaded_file)
    else:
        st.error("No file selected. Please upload a valid .zip file.")