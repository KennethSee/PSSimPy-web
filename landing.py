import streamlit as st
from utils.session import import_simulation_setting

st.write('# Welcome to *PSSimPy*: A Large Value Payment System Simulator')

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